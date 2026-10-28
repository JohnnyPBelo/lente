"""Abertura de ligações SQLite com PRAGMA de integridade e WAL."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def abrir_ligacao(caminho: Path | str) -> sqlite3.Connection:
    """Abre (ou cria) a BD com chaves estrangeiras e journal WAL activos.

    ``check_same_thread=False`` permite reutilizar a ligação no servidor ASGI
    (event loop + workers). ``synchronous=NORMAL`` com WAL reduz fsync por
    commit sem abdicar de durabilidade em falhas de processo.
    """
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    ligacao = sqlite3.connect(destino, check_same_thread=False)
    ligacao.row_factory = sqlite3.Row
    ligacao.execute("PRAGMA foreign_keys = ON")
    ligacao.execute("PRAGMA journal_mode = WAL")
    ligacao.execute("PRAGMA synchronous = NORMAL")
    ligacao.execute("PRAGMA busy_timeout = 5000")
    ligacao.execute("PRAGMA temp_store = MEMORY")
    return ligacao
