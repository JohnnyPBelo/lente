"""Filtro da biblioteca por etiqueta e tipo manual."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any


def _agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sugerir_tipo(
    ligacao: sqlite3.Connection,
    documento_id: int,
    tipo_sugerido: str,
) -> None:
    """Grava só ``tipo_sugerido``; nunca sobrescreve ``tipo`` manual."""
    ligacao.execute(
        """
        UPDATE documentos
        SET tipo_sugerido = ?, actualizado_em = ?
        WHERE id = ?
        """,
        (tipo_sugerido, _agora(), documento_id),
    )
    ligacao.commit()


def definir_tipo_manual(
    ligacao: sqlite3.Connection,
    documento_id: int,
    tipo: str,
) -> None:
    """Define o tipo escolhido pelo utilizador (filtro da biblioteca)."""
    ligacao.execute(
        """
        UPDATE documentos
        SET tipo = ?, actualizado_em = ?
        WHERE id = ?
        """,
        (tipo, _agora(), documento_id),
    )
    ligacao.commit()


def listar_documentos(
    ligacao: sqlite3.Connection,
    *,
    etiqueta: str | None = None,
    tipo: str | None = None,
) -> list[dict[str, Any]]:
    """Lista documentos; filtros usam etiqueta e tipo manual (não sugerido)."""
    sql = """
        SELECT
            d.id,
            d.caminho,
            d.titulo,
            d.tipo,
            d.tipo_sugerido,
            d.estado,
            d.sha256
        FROM documentos d
    """
    condicoes: list[str] = []
    params: list[Any] = []

    if etiqueta is not None:
        sql += """
            JOIN documento_etiquetas de ON de.documento_id = d.id
            JOIN etiquetas e ON e.id = de.etiqueta_id
        """
        condicoes.append("e.nome = ?")
        params.append(etiqueta)

    if tipo is not None:
        condicoes.append("d.tipo = ?")
        params.append(tipo)

    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)

    sql += " ORDER BY d.id ASC"

    linhas = ligacao.execute(sql, params).fetchall()
    saida: list[dict[str, Any]] = []
    for linha in linhas:
        doc_id = int(linha["id"])
        etiquetas = [
            r["nome"]
            for r in ligacao.execute(
                """
                SELECT e.nome
                FROM documento_etiquetas de
                JOIN etiquetas e ON e.id = de.etiqueta_id
                WHERE de.documento_id = ?
                ORDER BY e.nome ASC
                """,
                (doc_id,),
            ).fetchall()
        ]
        saida.append(
            {
                "id": doc_id,
                "caminho": linha["caminho"],
                "titulo": linha["titulo"],
                "tipo": linha["tipo"],
                "tipo_sugerido": linha["tipo_sugerido"],
                "etiquetas": etiquetas,
                "desactualizado": linha["estado"] == "desactualizado",
                "estado": linha["estado"],
                "sha256": linha["sha256"],
            }
        )
    return saida
