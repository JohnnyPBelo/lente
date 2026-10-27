"""``extrair()`` unificado: PDF com texto e classificação de imagem."""

from __future__ import annotations

from pathlib import Path

from engine.ingestao import extrair
from engine.ingestao.tipos import classificar

FIXTORES = Path(__file__).resolve().parents[1] / "fixtures" / "ingestao"
FRASE_AMOSTRA = "A frase sintetica da amostra PDF fica nesta linha."


def test_extrair_pdf_fixture() -> None:
    resultado = extrair(FIXTORES / "amostra_texto.pdf")
    assert resultado.tipo == "pdf"
    assert FRASE_AMOSTRA in resultado.texto
    assert resultado.precisa_ocr is False
    assert resultado.paginas is not None
    assert len(resultado.paginas) >= 1


def test_classificar_pdf_e_imagem() -> None:
    assert classificar(FIXTORES / "amostra_texto.pdf") == "pdf"
    assert classificar(FIXTORES / "amostra_scan.png") == "imagem"
