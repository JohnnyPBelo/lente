"""Etiquetas manuais N:N sobre documentos."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone


def _agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalizar(nome: str) -> str:
    texto = nome.strip()
    if not texto:
        raise ValueError("etiqueta vazia")
    return texto


def _obter_ou_criar(ligacao: sqlite3.Connection, nome: str) -> int:
    normalizado = _normalizar(nome)
    existente = ligacao.execute(
        "SELECT id FROM etiquetas WHERE nome = ?",
        (normalizado,),
    ).fetchone()
    if existente is not None:
        return int(existente["id"])
    cur = ligacao.execute(
        "INSERT INTO etiquetas (nome, criado_em) VALUES (?, ?)",
        (normalizado, _agora()),
    )
    return int(cur.lastrowid)


def definir_etiquetas(
    ligacao: sqlite3.Connection,
    documento_id: int,
    nomes: list[str],
) -> list[str]:
    """Substitui o conjunto de etiquetas do documento pelos nomes dados."""
    unicos: list[str] = []
    vistos: set[str] = set()
    for nome in nomes:
        n = _normalizar(nome)
        if n not in vistos:
            vistos.add(n)
            unicos.append(n)

    ligacao.execute(
        "DELETE FROM documento_etiquetas WHERE documento_id = ?",
        (documento_id,),
    )
    for nome in unicos:
        etiqueta_id = _obter_ou_criar(ligacao, nome)
        ligacao.execute(
            """
            INSERT INTO documento_etiquetas (documento_id, etiqueta_id)
            VALUES (?, ?)
            """,
            (documento_id, etiqueta_id),
        )
    ligacao.commit()
    return etiquetas_de(ligacao, documento_id)


def etiquetas_de(ligacao: sqlite3.Connection, documento_id: int) -> list[str]:
    """Lista os nomes de etiqueta do documento, ordenados."""
    linhas = ligacao.execute(
        """
        SELECT e.nome
        FROM documento_etiquetas de
        JOIN etiquetas e ON e.id = de.etiqueta_id
        WHERE de.documento_id = ?
        ORDER BY e.nome ASC
        """,
        (documento_id,),
    ).fetchall()
    return [linha["nome"] for linha in linhas]
