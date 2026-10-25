"""Regressões REG-ING-001…004: extracção txt/md/docx e registo na fila."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from engine.armazenamento.ligacao import abrir_ligacao
from engine.armazenamento.migracoes import aplicar_migracoes
from engine.ingestao import extrair
from engine.ingestao.hash import sha256_ficheiro
from engine.ingestao.registo import registar_ficheiro, registar_texto
from engine.ingestao.tipos import FicheiroInexistente


FIXTORES = Path(__file__).resolve().parents[1] / "fixtures" / "ingestao"
PARAGRAFO_MD = (
    "O parágrafo conhecido da amostra Markdown fica aqui para a extracção."
)


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


def test_reg_ing_001(ligacao: sqlite3.Connection, tmp_path: Path) -> None:
    """Texto colado vira documento na fila; caminho inexistente → erro tipado."""
    destino = tmp_path / "colagem.txt"
    texto = "Bloco de texto plano sintético para colagem na biblioteca."

    registo = registar_texto(ligacao, texto, destino)
    assert destino.is_file()
    assert destino.read_text(encoding="utf-8") == texto

    linha = ligacao.execute(
        "SELECT id, caminho, estado FROM documentos WHERE id = ?",
        (registo.id,),
    ).fetchone()
    assert linha is not None
    assert linha["caminho"] == str(destino.resolve())
    assert linha["estado"] == "a_indexar"

    fila = ligacao.execute(
        "SELECT documento_id, estado FROM fila WHERE documento_id = ?",
        (registo.id,),
    ).fetchone()
    assert fila is not None
    assert fila["estado"] == "pendente"

    with pytest.raises(FicheiroInexistente):
        extrair(tmp_path / "nao-existe.md")


def test_reg_ing_002() -> None:
    """Markdown sintético: parágrafo conhecido e títulos não vazios."""
    amostra = FIXTORES / "amostra.md"
    resultado = extrair(amostra)
    assert PARAGRAFO_MD in resultado.texto
    assert resultado.titulos
    assert any(
        isinstance(t.get("titulo"), str) and t["titulo"]
        for t in resultado.titulos
    )
    digest = sha256_ficheiro(amostra)
    assert len(digest) == 64
    assert digest == digest.lower()
    assert all(c in "0123456789abcdef" for c in digest)
    assert digest == sha256_ficheiro(amostra)


def test_reg_ing_003(tmp_path: Path) -> None:
    """UTF-8 e fallback latin-1: texto legível, sem silêncio no encoding."""
    utf8 = FIXTORES / "amostra.txt"
    resultado_utf8 = extrair(utf8)
    assert "café" in resultado_utf8.texto
    assert "açúcar" in resultado_utf8.texto

    latin1 = tmp_path / "amostra-latin1.txt"
    latin1.write_bytes("Olá com bytes latin-1: café".encode("latin-1"))
    resultado_latin1 = extrair(latin1)
    assert "café" in resultado_latin1.texto
    assert "Olá" in resultado_latin1.texto


def test_reg_ing_004() -> None:
    """docx sintético: ordem dos parágrafos preservada no texto plano."""
    resultado = extrair(FIXTORES / "amostra.docx")
    primeiro = resultado.texto.find("Primeiro parágrafo sintético do docx.")
    segundo = resultado.texto.find("Segundo parágrafo sintético do docx.")
    terceiro = resultado.texto.find("Terceiro parágrafo sintético do docx.")
    assert primeiro != -1 and segundo != -1 and terceiro != -1
    assert primeiro < segundo < terceiro
