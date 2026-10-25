"""Fixtures de armazenamento: directório temporário, nunca ``data/`` do clone."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def caminho_tmp(tmp_path: Path) -> Path:
    """Caminho de um SQLite temporário por teste."""
    pasta = tmp_path / "data"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / "lente.sqlite"
