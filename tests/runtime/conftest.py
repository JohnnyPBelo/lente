"""Fixtures do runtime: directórios temporários e porto livre."""

from __future__ import annotations

import socket
from pathlib import Path

import pytest


@pytest.fixture
def raiz_tmp(tmp_path: Path) -> Path:
    """Raiz de projecto sintética com docs/origem/plano.md (marcador)."""
    marcador = tmp_path / "docs" / "origem"
    marcador.mkdir(parents=True)
    (marcador / "plano.md").write_text("# plano\n", encoding="utf-8")
    (tmp_path / "data").mkdir()
    (tmp_path / "models").mkdir()
    return tmp_path


@pytest.fixture
def porto_livre() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@pytest.fixture
def caminho_tmp(tmp_path: Path) -> Path:
    pasta = tmp_path / "data"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / "lente.sqlite"
