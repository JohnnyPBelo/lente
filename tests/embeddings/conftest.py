"""Fixtures de embeddings: SQLite temporário e sessão double."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.embeddings.carregar import SessaoEmbedding
from tests.embeddings.apoio import sessao_dupla


@pytest.fixture
def caminho_tmp(tmp_path: Path) -> Path:
    pasta = tmp_path / "data"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / "lente.sqlite"


@pytest.fixture
def sessao_embedding() -> SessaoEmbedding:
    return sessao_dupla()
