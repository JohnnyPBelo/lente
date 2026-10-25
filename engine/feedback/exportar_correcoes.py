"""Exportação do conjunto de correções (JSON do esquema, sem pesos LoRA)."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from engine.feedback.registar import listar_pares
from engine.feedback.schema_correcoes import (
    CHAVE_CORRECOES,
    CHAVE_FORMATO,
    CHAVE_MODELO,
    FORMATO_VERSAO,
)
from engine.juiz.caminhos import MODELO_ID


def _agora() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def deduplicar_correcoes(
    pares: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Pares com o mesmo ``hash_par`` entram uma vez (REQ-FBK-011)."""
    vistos: set[str] = set()
    unicos: list[dict[str, Any]] = []
    for par in pares:
        digest = str(par["hash_par"])
        if digest in vistos:
            continue
        vistos.add(digest)
        unicos.append(
            {
                "pergunta": str(par["pergunta"]),
                "trecho": str(par["trecho"]),
                "etiqueta": str(par["etiqueta"]),
                "lente": str(par["lente"]),
                "hash_par": digest,
            }
        )
    return unicos


def exportar_correcoes(
    ligacao: sqlite3.Connection,
    *,
    modelo_base_id: str | None = None,
    incluir_exported_at: bool = True,
) -> dict[str, Any]:
    """Devolve o pacote JSON com as chaves do esquema (sem pesos)."""
    correcoes = deduplicar_correcoes(listar_pares(ligacao))
    pacote: dict[str, Any] = {
        CHAVE_FORMATO: FORMATO_VERSAO,
        CHAVE_MODELO: modelo_base_id or MODELO_ID,
        CHAVE_CORRECOES: correcoes,
    }
    if incluir_exported_at:
        pacote["exported_at"] = _agora()
    return pacote
