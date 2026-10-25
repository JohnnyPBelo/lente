"""Leitura paginada do diário local."""

from __future__ import annotations

import json
import sqlite3
from typing import Any


def ler_diario(
    ligacao: sqlite3.Connection,
    *,
    depois_de: int | None = None,
    limite: int = 100,
) -> list[dict[str, Any]]:
    """Devolve entradas por ordem de inserção (id crescente)."""
    if limite < 1:
        raise ValueError("limite tem de ser pelo menos 1")
    if depois_de is None:
        linhas = ligacao.execute(
            """
            SELECT id, tipo, payload_json, criado_em
            FROM diario
            ORDER BY id ASC
            LIMIT ?
            """,
            (limite,),
        ).fetchall()
    else:
        linhas = ligacao.execute(
            """
            SELECT id, tipo, payload_json, criado_em
            FROM diario
            WHERE id > ?
            ORDER BY id ASC
            LIMIT ?
            """,
            (depois_de, limite),
        ).fetchall()
    saida: list[dict[str, Any]] = []
    for linha in linhas:
        saida.append(
            {
                "id": int(linha["id"]),
                "tipo": linha["tipo"],
                "payload": json.loads(linha["payload_json"]),
                "criado_em": linha["criado_em"],
            }
        )
    return saida
