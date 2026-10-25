"""Helpers mínimos: abrir a BD e consultar o estado do esquema."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from engine.armazenamento.caminho import caminho_sqlite
from engine.armazenamento.ligacao import abrir_ligacao
from engine.armazenamento.migracoes import aplicar_migracoes


def abrir(
    caminho: Path | str | None = None,
    *,
    aplicar: bool = True,
) -> sqlite3.Connection:
    """Abre a ligação; por omissão aplica migrações pendentes antes."""
    destino = Path(caminho) if caminho is not None else caminho_sqlite()
    if aplicar:
        aplicar_migracoes(destino)
    return abrir_ligacao(destino)


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
