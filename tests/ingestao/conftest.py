"""Fixtures de ingestão: SQLite temporário migrado."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from engine.armazenamento.ligacao import abrir_ligacao
from engine.armazenamento.migracoes import aplicar_migracoes


@pytest.fixture
def caminho_tmp(tmp_path: Path) -> Path:
    pasta = tmp_path / "data"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / "lente.sqlite"


@pytest.fixture
def ligacao(caminho_tmp: Path) -> sqlite3.Connection:
    aplicar_migracoes(caminho_tmp)
    lig = abrir_ligacao(caminho_tmp)
    yield lig
    lig.close()
