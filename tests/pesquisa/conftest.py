"""Fixtures de pesquisa: SQLite temporário com migrações (nunca ``data/``)."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.armazenamento.repositorio import abrir


@pytest.fixture
def caminho_tmp(tmp_path: Path) -> Path:
    """Caminho de um SQLite temporário por teste."""
    pasta = tmp_path / "data"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / "lente.sqlite"


@pytest.fixture
def ligacao(caminho_tmp: Path):
    """Ligação migrada pronta para indexar e consultar."""
    conn = abrir(caminho_tmp)
    yield conn
    conn.close()


def semear_bloco(
    ligacao,
    texto: str,
    *,
    caminho: str = "/tmp/lente-pesquisa.txt",
    ordem: int = 0,
) -> tuple[int, int, int]:
    """Insere documento + hash activo + bloco. Devolve (bloco_id, documento_id, hash_id)."""
    agora = "2026-10-25T00:00:00Z"
    ligacao.execute(
        "INSERT INTO documentos ("
        "caminho, titulo, tipo, sha256, estado, criado_em, actualizado_em"
        ") VALUES (?, 't', 'txt', 'abc', 'ok', ?, ?)",
        (caminho, agora, agora),
    )
    documento_id = int(ligacao.execute("SELECT last_insert_rowid()").fetchone()[0])
    ligacao.execute(
        "INSERT INTO documento_hashes (documento_id, sha256, visto_em, activa) "
        "VALUES (?, 'abc', ?, 1)",
        (documento_id, agora),
    )
    hash_id = int(ligacao.execute("SELECT last_insert_rowid()").fetchone()[0])
    ligacao.execute(
        "INSERT INTO blocos ("
        "documento_id, hash_id, ordem, texto, offset_inicio, offset_fim, tokens_aprox"
        ") VALUES (?, ?, ?, ?, 0, ?, ?)",
        (documento_id, hash_id, ordem, texto, len(texto), max(1, len(texto.split()))),
    )
    bloco_id = int(ligacao.execute("SELECT last_insert_rowid()").fetchone()[0])
    ligacao.commit()
    return bloco_id, documento_id, hash_id
