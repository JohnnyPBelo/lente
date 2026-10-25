"""Reabrir dossier: lê a fotografia; nunca corre modelos."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from engine.dossier.fechar import resolver_id
from engine.dossier.integridade import fonte_alterada as _fonte_alterada


def _carregar_linha(
    ligacao: sqlite3.Connection, dossier_id: int
) -> tuple:
    linha = ligacao.execute(
        """
        SELECT
            id, conversa_id, titulo, fechado_em,
            perguntas_json, frases_json, ficheiros_json,
            versao_embedding, versao_juiz, versao_e2b, export_json
        FROM dossiers
        WHERE id = ?
        """,
        (dossier_id,),
    ).fetchone()
    if linha is None:
        raise ValueError(f"Dossier inexistente: {dossier_id}")
    return linha


def fotografia_canonica(
    ligacao: sqlite3.Connection, dossier_id: int | str
) -> dict[str, Any]:
    """Devolve o JSON alinhado a ``dossier.schema.json`` (sem correr modelos)."""
    row_id = resolver_id(dossier_id)
    linha = _carregar_linha(ligacao, row_id)
    export_json = linha[10]
    if export_json:
        return json.loads(export_json)

    perguntas = json.loads(linha[4])
    frases = json.loads(linha[5])
    ficheiros = json.loads(linha[6])
    return {
        "format_version": "1",
        "id": f"dos_{row_id}",
        "titulo": linha[2],
        "conversa_id": linha[1],
        "fechado_em": linha[3],
        "perguntas": perguntas,
        "frases_aceites": frases,
        "ficheiros": ficheiros,
        "versoes_modelo": {
            "embedding": linha[7],
            "juiz": linha[8],
            "e2b": linha[9],
        },
    }


def reabrir_dossier(
    ligacao: sqlite3.Connection, dossier_id: int | str
) -> dict[str, Any]:
    """Lê a fotografia. Expõe ``fonte_alterada`` se o hash em disco divergir.

    Não chama EmbeddingGemma, juiz nem E2B — só SQLite e, para integridade,
    o SHA-256 dos bytes em disco.
    """
    foto = fotografia_canonica(ligacao, dossier_id)
    ficheiros = list(foto.get("ficheiros") or [])
    alterada = _fonte_alterada(ficheiros)
    frases_aceites = list(foto.get("frases_aceites") or [])

    # Contrato HTTP (GET): fonte_alterada + frases; molde canónico no schema.
    frases_http: list[dict[str, Any]] = []
    for frase in frases_aceites:
        frases_http.append(
            {
                "texto": frase.get("frase_resposta") or frase.get("trecho_literal"),
                "trecho": frase.get("trecho_literal"),
                "trecho_literal": frase.get("trecho_literal"),
                "ficheiro": frase.get("ficheiro"),
                "documento_id": None,
                "pagina": frase.get("pagina"),
                "offset_inicio": frase.get("offset_inicio"),
                "offset_fim": frase.get("offset_fim"),
                "caixas": frase.get("caixas") or [],
                "hash_sha256_fecho": frase.get("sha256_ficheiro"),
                "sha256_ficheiro": frase.get("sha256_ficheiro"),
                "score_juiz": frase.get("pontuacao_juiz"),
                "pontuacao_juiz": frase.get("pontuacao_juiz"),
                "indice": frase.get("indice"),
            }
        )

    return {
        "id": foto.get("id"),
        "chat_id": foto.get("conversa_id"),
        "conversa_id": foto.get("conversa_id"),
        "titulo": foto.get("titulo"),
        "fechado_em": foto.get("fechado_em"),
        "fonte_alterada": alterada,
        "perguntas": foto.get("perguntas"),
        "frases_aceites": frases_aceites,
        "frases": frases_http,
        "ficheiros": ficheiros,
        "versoes_modelo": foto.get("versoes_modelo"),
        "fotografia": foto,
    }
