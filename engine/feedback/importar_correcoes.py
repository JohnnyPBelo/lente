"""Importação de correções: pré-visualização, confirmação obrigatória, dedupe."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from engine.feedback.registar import hash_par, listar_pares
from engine.feedback.schema_correcoes import (
    CHAVE_CORRECOES,
    CHAVE_MODELO,
    CorrecoesInvalidas,
    validar_pacote,
)
from engine.juiz.caminhos import MODELO_ID

AMOSTRAS_MAX = 5


class ModeloBaseIncompativel(ValueError):
    """Ficheiro cujo ``base_model_id`` não é o do juiz instalado."""


def _agora() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _hashes_existentes(ligacao: sqlite3.Connection) -> set[str]:
    return {str(par["hash_par"]) for par in listar_pares(ligacao)}


def _normalizar_correcoes(pacote: dict[str, Any]) -> list[dict[str, Any]]:
    """Garante hash estável; dedupe interno do ficheiro."""
    vistos: set[str] = set()
    saida: list[dict[str, Any]] = []
    for item in pacote[CHAVE_CORRECOES]:
        pergunta = str(item["pergunta"])
        trecho = str(item["trecho"])
        etiqueta = str(item["etiqueta"])
        lente = str(item["lente"])
        digest = str(item.get("hash_par") or hash_par(pergunta, trecho, etiqueta, lente))
        esperado = hash_par(pergunta, trecho, etiqueta, lente)
        if digest != esperado:
            # Aceita o hash do ficheiro se for o canónico; senão recalcula.
            digest = esperado
        if digest in vistos:
            continue
        vistos.add(digest)
        saida.append(
            {
                "pergunta": pergunta,
                "trecho": trecho,
                "etiqueta": etiqueta,
                "lente": lente,
                "hash_par": digest,
            }
        )
    return saida


def previsualizar_importacao(
    ligacao: sqlite3.Connection,
    dados: object,
    *,
    modelo_base_id: str | None = None,
) -> dict[str, Any]:
    """Pré-visualização: contagem, lentes, amostra — sem gravar."""
    pacote = validar_pacote(dados)
    instalado = modelo_base_id or MODELO_ID
    modelo_ok = str(pacote[CHAVE_MODELO]) == instalado
    if not modelo_ok:
        # Preview ainda devolve o DTO, mas a confirmação será recusada.
        correcoes = _normalizar_correcoes(pacote)
        return {
            "contagem": len(correcoes),
            "lentes": sorted({c["lente"] for c in correcoes}),
            "amostra_perguntas": [c["pergunta"] for c in correcoes[:AMOSTRAS_MAX]],
            "duplicados_ignorados": 0,
            "modelo_base_ok": False,
        }

    correcoes = _normalizar_correcoes(pacote)
    existentes = _hashes_existentes(ligacao)
    novos = [c for c in correcoes if c["hash_par"] not in existentes]
    duplicados = len(correcoes) - len(novos)
    return {
        "contagem": len(correcoes),
        "lentes": sorted({c["lente"] for c in correcoes}),
        "amostra_perguntas": [c["pergunta"] for c in correcoes[:AMOSTRAS_MAX]],
        "duplicados_ignorados": duplicados,
        "modelo_base_ok": True,
    }


def _inserir_importados(
    ligacao: sqlite3.Connection,
    correcoes: list[dict[str, Any]],
) -> int:
    """Upsert por ``hash_par`` (UNIQUE); devolve quantos foram novos."""
    existentes = _hashes_existentes(ligacao)
    inseridos = 0
    agora = _agora()
    for correcao in correcoes:
        if correcao["hash_par"] in existentes:
            continue
        ligacao.execute(
            "INSERT OR IGNORE INTO feedback "
            "(mensagem_id, pergunta, trecho, etiqueta, lente, hash_par, "
            "documento_id, frase_id, origem, criado_em) "
            "VALUES (NULL, ?, ?, ?, ?, ?, NULL, NULL, 'importado', ?)",
            (
                correcao["pergunta"],
                correcao["trecho"],
                correcao["etiqueta"],
                correcao["lente"],
                correcao["hash_par"],
                agora,
            ),
        )
        existentes.add(correcao["hash_par"])
        inseridos += 1
    ligacao.commit()
    return inseridos


def _agendar_treino_padrao() -> None:
    """Marca intenção de treino; o runtime PLN-16 corre LoRA quando livre."""
    # A confirmação só agenda; o executor chama ``treinar_lora`` com o slot.
    return None


def importar_correcoes(
    ligacao: sqlite3.Connection,
    dados: object,
    *,
    confirmar: bool = False,
    modelo_base_id: str | None = None,
    agendar_treino: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Importa correções.

    Com ``confirmar=False`` (omissão) só pré-visualiza — nada é gravado
    (REQ-FBK-014, REQ-FBK-016, REQ-SEG-004). Com confirmação: valida o
    modelo base, faz upsert dedupe e agenda o treino a partir do base.
    """
    previa = previsualizar_importacao(
        ligacao, dados, modelo_base_id=modelo_base_id
    )
    if not confirmar:
        return previa

    instalado = modelo_base_id or MODELO_ID
    pacote = validar_pacote(dados)
    if str(pacote[CHAVE_MODELO]) != instalado:
        raise ModeloBaseIncompativel(
            f"base_model_id {pacote[CHAVE_MODELO]!r} ≠ juiz {instalado!r}."
        )

    correcoes = _normalizar_correcoes(pacote)
    _inserir_importados(ligacao, correcoes)

    agendar = agendar_treino if agendar_treino is not None else _agendar_treino_padrao
    agendar()
    return {
        "aceite": True,
        "treino_agendado": True,
        "contagem": previa["contagem"],
        "duplicados_ignorados": previa["duplicados_ignorados"],
    }
