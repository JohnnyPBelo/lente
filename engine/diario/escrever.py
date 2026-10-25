"""Escrita do diário local: só INSERT (append-only)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Mapping

TIPOS_ACEITES = frozenset(
    {"procura", "abertura", "feedback", "fecho_dossier"}
)


class TipoDiarioInvalido(ValueError):
    """Tipo de entrada fora do conjunto aceite pelo esquema."""


def _agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def acrescentar(
    ligacao: sqlite3.Connection,
    tipo: str,
    payload: Mapping[str, Any] | None = None,
) -> int:
    """Insere uma entrada. Não actualiza nem apaga linhas existentes."""
    if tipo not in TIPOS_ACEITES:
        raise TipoDiarioInvalido(tipo)
    corpo = dict(payload or {})
    cur = ligacao.execute(
        "INSERT INTO diario (tipo, payload_json, criado_em) VALUES (?, ?, ?)",
        (tipo, json.dumps(corpo, ensure_ascii=False, separators=(",", ":")), _agora()),
    )
    ligacao.commit()
    return int(cur.lastrowid)


def registar_procura(
    ligacao: sqlite3.Connection,
    payload: Mapping[str, Any] | None = None,
) -> int:
    return acrescentar(ligacao, "procura", payload)


def registar_abertura(
    ligacao: sqlite3.Connection,
    payload: Mapping[str, Any] | None = None,
) -> int:
    return acrescentar(ligacao, "abertura", payload)


def registar_feedback(
    ligacao: sqlite3.Connection,
    payload: Mapping[str, Any] | None = None,
) -> int:
    return acrescentar(ligacao, "feedback", payload)


def registar_fecho_dossier(
    ligacao: sqlite3.Connection,
    payload: Mapping[str, Any] | None = None,
) -> int:
    return acrescentar(ligacao, "fecho_dossier", payload)
