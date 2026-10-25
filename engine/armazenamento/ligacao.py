"""Abertura de ligações SQLite com PRAGMA de integridade e WAL."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def abrir_ligacao(caminho: Path | str) -> sqlite3.Connection:
    """Abre (ou cria) a BD com chaves estrangeiras e journal WAL activos."""
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    ligacao = sqlite3.connect(destino)
    ligacao.row_factory = sqlite3.Row
    ligacao.execute("PRAGMA foreign_keys = ON")
    ligacao.execute("PRAGMA journal_mode = WAL")
    return ligacao
