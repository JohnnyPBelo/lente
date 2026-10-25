"""Registo de feedback: Acertou / Corrigir / Descartar (sem slot pesado)."""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from engine.escalonador.slot import SlotPesado

BOOST_POSITIVO = 1.0
PENALIZACAO_NEGATIVO = 1.0


def _agora() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def hash_par(pergunta: str, trecho: str, etiqueta: str, lente: str) -> str:
    """Hash estável do par (pergunta + trecho + etiqueta + lente)."""
    material = f"{pergunta}\0{trecho}\0{etiqueta}\0{lente}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _inserir_par(
    ligacao: sqlite3.Connection,
    *,
    mensagem_id: int | None,
    pergunta: str,
    trecho: str,
    etiqueta: str,
    lente: str,
    origem: str = "local",
) -> None:
    digest = hash_par(pergunta, trecho, etiqueta, lente)
    ligacao.execute(
        "INSERT OR IGNORE INTO feedback "
        "(mensagem_id, pergunta, trecho, etiqueta, lente, hash_par, "
        "documento_id, frase_id, origem, criado_em) "
        "VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?)",
        (mensagem_id, pergunta, trecho, etiqueta, lente, digest, origem, _agora()),
    )
    ligacao.commit()


def _garantir_sem_slot_search(slot: SlotPesado | None) -> None:
    """Feedback imediato é leve: nunca adquire o slot de procura."""
    del slot  # explícito: o parâmetro existe só para a API e para testes


def registar_descartar(
    ligacao: sqlite3.Connection,
    *,
    mensagem_id: int | None = None,
    pergunta: str = "",
    trechos_mostrados: Sequence[str] = (),
    lente: str = "investigar",
    slot: SlotPesado | None = None,
) -> None:
    """Descartar: não cria pares de treino nem altera pesos."""
    _garantir_sem_slot_search(slot)
    del mensagem_id, pergunta, trechos_mostrados, lente


def registar_acertou(
    ligacao: sqlite3.Connection,
    *,
    mensagem_id: int | None,
    pergunta: str,
    trechos_mostrados: Sequence[str],
    lente: str,
    slot: SlotPesado | None = None,
) -> None:
    """Acertou: marca os trechos mostrados como positivos."""
    _garantir_sem_slot_search(slot)
    for trecho in trechos_mostrados:
        _inserir_par(
            ligacao,
            mensagem_id=mensagem_id,
            pergunta=pergunta,
            trecho=trecho,
            etiqueta="positivo",
            lente=lente,
        )


def registar_corrigir(
    ligacao: sqlite3.Connection,
    *,
    mensagem_id: int | None,
    pergunta: str,
    marcas_resposta: Sequence[str],
    selecao: str,
    lente: str,
    slot: SlotPesado | None = None,
) -> None:
    """Corrigir: marcas da resposta negativas; selecção positiva."""
    _garantir_sem_slot_search(slot)
    for trecho in marcas_resposta:
        _inserir_par(
            ligacao,
            mensagem_id=mensagem_id,
            pergunta=pergunta,
            trecho=trecho,
            etiqueta="negativo",
            lente=lente,
        )
    _inserir_par(
        ligacao,
        mensagem_id=mensagem_id,
        pergunta=pergunta,
        trecho=selecao,
        etiqueta="positivo",
        lente=lente,
    )


def listar_pares(ligacao: sqlite3.Connection) -> list[dict[str, Any]]:
    """Devolve os pares de feedback persistidos."""
    linhas = ligacao.execute(
        "SELECT mensagem_id, pergunta, trecho, etiqueta, lente, hash_par, origem "
        "FROM feedback ORDER BY id"
    ).fetchall()
    return [
        {
            "mensagem_id": row[0],
            "pergunta": row[1],
            "trecho": row[2],
            "etiqueta": row[3],
            "lente": row[4],
            "hash_par": row[5],
            "origem": row[6],
        }
        for row in linhas
    ]


def ajustar_pontuacoes(
    pergunta: str,
    candidatos: Sequence[tuple[str, float]],
    *,
    pares: Sequence[Mapping[str, Any]],
) -> list[tuple[str, float]]:
    """Efeito imediato: sobe confirmados e desce rejeitados (REQ-JUI-004).

    Só afecta candidatos já trazidos; não toca em EmbeddingGemma nem E2B.
    A integração fina com a fusão fica em PLN-09 (`feedback_runtime`).
    """
    pergunta_norm = pergunta.casefold().strip()
    boost: dict[str, float] = {}
    for par in pares:
        if str(par["pergunta"]).casefold().strip() != pergunta_norm:
            # Pergunta «muito parecida»: overlap léxico simples.
            palavras_p = set(pergunta_norm.split())
            palavras_q = set(str(par["pergunta"]).casefold().split())
            if not palavras_p or len(palavras_p & palavras_q) / len(palavras_p) < 0.5:
                continue
        trecho = str(par["trecho"])
        if par["etiqueta"] == "positivo":
            boost[trecho] = boost.get(trecho, 0.0) + BOOST_POSITIVO
        else:
            boost[trecho] = boost.get(trecho, 0.0) - PENALIZACAO_NEGATIVO

    return [(trecho, score + boost.get(trecho, 0.0)) for trecho, score in candidatos]
