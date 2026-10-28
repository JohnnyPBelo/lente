"""Helpers mínimos: abrir a BD e consultar o estado do esquema."""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from engine.armazenamento.caminho import caminho_sqlite
from engine.armazenamento.ligacao import abrir_ligacao
from engine.armazenamento.migracoes import aplicar_migracoes

# Evita reabrir+reler SQL de esquema a cada pedido HTTP.
_MIGRADO: set[str] = set()
_MIGRADO_LOCK = threading.Lock()


def _chave(caminho: Path) -> str:
    return str(caminho.resolve())


def garantir_migracoes(caminho: Path | str) -> None:
    """Aplica migrações pendentes uma vez por processo/caminho."""
    destino = Path(caminho)
    chave = _chave(destino)
    if chave in _MIGRADO:
        return
    with _MIGRADO_LOCK:
        if chave in _MIGRADO:
            return
        aplicar_migracoes(destino)
        _MIGRADO.add(chave)


def abrir(
    caminho: Path | str | None = None,
    *,
    aplicar: bool = True,
) -> sqlite3.Connection:
    """Abre a ligação; por omissão aplica migrações pendentes antes."""
    destino = Path(caminho) if caminho is not None else caminho_sqlite()
    if aplicar:
        garantir_migracoes(destino)
    return abrir_ligacao(destino)


@contextmanager
def ligacao_temporaria(
    caminho: Path | str | None = None,
    *,
    aplicar: bool = True,
) -> Iterator[sqlite3.Connection]:
    """Abre e fecha a ligação — evita avisos de BD por fechar e fugas de fd."""
    ligacao = abrir(caminho, aplicar=aplicar)
    try:
        yield ligacao
    finally:
        ligacao.close()


def estado_esquema(caminho: Path | str | None = None) -> dict[str, object]:
    """Devolve ``user_version`` e o conjunto de tabelas de utilizador."""
    destino = Path(caminho) if caminho is not None else caminho_sqlite(criar_pasta=False)
    with abrir_ligacao(destino) as ligacao:
        versao = int(ligacao.execute("PRAGMA user_version").fetchone()[0])
        tabelas = [
            linha[0]
            for linha in ligacao.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
                "ORDER BY name"
            ).fetchall()
        ]
    return {"user_version": versao, "tabelas": tabelas}


def limpar_cache_migracoes() -> None:
    """Esvazia o cache de migrações (testes)."""
    _MIGRADO.clear()
