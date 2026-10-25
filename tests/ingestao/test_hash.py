"""Regressão REG-ING-008: SHA-256 e marcação desactualizado."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from engine.armazenamento.ligacao import abrir_ligacao
from engine.armazenamento.migracoes import aplicar_migracoes
from engine.ingestao.hash import sha256_ficheiro
from engine.ingestao.registo import registar_ficheiro, verificar_actualidade


FIXTORES = Path(__file__).resolve().parents[1] / "fixtures" / "ingestao"


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


def test_reg_ing_008(ligacao: sqlite3.Connection, tmp_path: Path) -> None:
    """SHA-256 de 64 hex; bytes alterados → desactualizado, sem índice falso."""
    origem = FIXTORES / "amostra.txt"
    destino = tmp_path / "documento.txt"
    destino.write_bytes(origem.read_bytes())

    registo = registar_ficheiro(ligacao, destino)
    digest = sha256_ficheiro(destino)
    assert len(digest) == 64
    assert digest == digest.lower()
    assert registo.sha256 == digest

    linha = ligacao.execute(
        "SELECT sha256, estado FROM documentos WHERE id = ?",
        (registo.id,),
    ).fetchone()
    assert linha["sha256"] == digest
    assert linha["estado"] == "a_indexar"

    hash_activa = ligacao.execute(
        "SELECT sha256, activa FROM documento_hashes "
        "WHERE documento_id = ? AND activa = 1",
        (registo.id,),
    ).fetchone()
    assert hash_activa is not None
    assert hash_activa["sha256"] == digest

    destino.write_text(
        "Conteúdo alterado em disco para forçar desactualizado.\n",
        encoding="utf-8",
    )
    estado = verificar_actualidade(ligacao, registo.id)
    assert estado == "desactualizado"

    depois = ligacao.execute(
        "SELECT sha256, estado FROM documentos WHERE id = ?",
        (registo.id,),
    ).fetchone()
    assert depois["estado"] == "desactualizado"
    # O SHA gravado (versão indexável) não muda em silêncio para o novo disco:
    # o índice antigo deixa de se tratar como actual.
    assert depois["sha256"] == digest
    assert depois["sha256"] != sha256_ficheiro(destino)


def test_mesmo_conteudo_dois_caminhos(ligacao: sqlite3.Connection, tmp_path: Path) -> None:
    """Mesmo conteúdo → mesmo SHA; caminhos distintos → dois documentos."""
    bytes_iguais = b"Conteudo sintetico partilhado entre dois caminhos.\n"
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_bytes(bytes_iguais)
    b.write_bytes(bytes_iguais)

    ra = registar_ficheiro(ligacao, a)
    rb = registar_ficheiro(ligacao, b)
    assert ra.sha256 == rb.sha256 == sha256_ficheiro(a)
    assert ra.id != rb.id

    total = ligacao.execute("SELECT COUNT(*) AS n FROM documentos").fetchone()["n"]
    assert total == 2
