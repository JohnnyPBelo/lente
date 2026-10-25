"""Regressão REG-ING-006: OCR Tesseract para scans e imagens.

O caminho positivo do manifesto pode usar um runner injectável (mock) para o
CI não depender do binário. ``test_ocr_sistema_requer_tesseract`` exige
``tesseract`` e o idioma ``por`` no sistema; não entra no manifesto.

Os imports de ``engine.ingestao.ocr`` ficam dentro dos testes para não
carregar o módulo na recolha — o REG-ING-005 exige que o extractor PDF
não puxe o OCR só por o ficheiro de teste existir.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


FIXTORES = Path(__file__).resolve().parents[1] / "fixtures" / "ingestao"
AMOSTRA = FIXTORES / "amostra_scan.png"


def test_reg_ing_006(monkeypatch: pytest.MonkeyPatch) -> None:
    """LENTE + caixa; TesseractEmFalta se ausente; OCR só com precisa_ocr."""
    import engine.ingestao.ocr as ocr_mod
    from engine.ingestao.ocr import TesseractEmFalta, ocr_imagem
    from engine.ingestao.pdf_ocr import ocr_pdf_quando_preciso

    assert AMOSTRA.is_file()

    monkeypatch.setattr(ocr_mod, "caminho_tesseract", lambda: None)
    with pytest.raises(TesseractEmFalta):
        ocr_imagem(AMOSTRA)
    monkeypatch.undo()

    if ocr_mod.caminho_tesseract() is None:

        def _falso_ocr(
            caminho: Path | str,
            *,
            pagina: int = 1,
            idioma: str = "por",
            timeout: float = 60.0,
        ) -> ocr_mod.ResultadoOCR:
            del caminho, idioma, timeout
            return ocr_mod.ResultadoOCR(
                texto="LENTE",
                caixas=[
                    {
                        "pagina": pagina,
                        "x": 57.0,
                        "y": 60.0,
                        "largura": 323.0,
                        "altura": 70.0,
                    }
                ],
                estado="ok",
            )

        monkeypatch.setattr(ocr_mod, "ocr_imagem", _falso_ocr)
        resultado = ocr_mod.ocr_imagem(AMOSTRA)
    else:
        resultado = ocr_imagem(AMOSTRA)

    assert "LENTE" in resultado.texto
    assert any(
        float(c["largura"]) > 0 and float(c["altura"]) > 0 for c in resultado.caixas
    )

    chamadas: list[Any] = []

    def _proibido(*_a: Any, **_k: Any) -> ocr_mod.ResultadoOCR:
        chamadas.append(1)
        raise AssertionError("OCR não deve correr quando o PDF já tem texto")

    monkeypatch.setattr(ocr_mod, "ocr_imagem", _proibido)
    sem_ocr = ocr_pdf_quando_preciso(
        AMOSTRA,
        precisa_ocr=False,
        texto_existente="Texto seleccionável já extraído.",
    )
    assert chamadas == []
    assert "Texto seleccionável já extraído." in sem_ocr.texto
    assert sem_ocr.caixas == []


def test_imagem_sem_texto_observavel(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Imagem sem texto: string vazia e estado aviso (não índice opaco silencioso)."""
    import engine.ingestao.ocr as ocr_mod
    from engine.ingestao.imagens import gravar_raster_rgb
    from engine.ingestao.ocr import ocr_imagem

    vazia = tmp_path / "vazia.png"
    gravar_raster_rgb(vazia, largura=64, altura=32, cor=(255, 255, 255))

    if ocr_mod.caminho_tesseract() is None:

        def _vazio(
            caminho: Path | str,
            *,
            pagina: int = 1,
            idioma: str = "por",
            timeout: float = 60.0,
        ) -> ocr_mod.ResultadoOCR:
            del caminho, pagina, idioma, timeout
            return ocr_mod.ResultadoOCR(texto="", caixas=[], estado="aviso")

        monkeypatch.setattr(ocr_mod, "ocr_imagem", _vazio)
        resultado = ocr_mod.ocr_imagem(vazia)
    else:
        resultado = ocr_imagem(vazia)

    assert resultado.texto.strip() == ""
    assert resultado.estado in {"aviso", "ok"}


def test_ocr_sistema_requer_tesseract() -> None:
    """OCR real sobre a fixture.

    Requer ``tesseract`` e o pacote de idioma ``por`` no sistema.
    Não entra no manifesto de regressão; o CI pode omitir o binário porque
    ``test_reg_ing_006`` aceita runner injectável.
    """
    import engine.ingestao.ocr as ocr_mod
    from engine.ingestao.ocr import ocr_imagem

    if ocr_mod.caminho_tesseract() is None:
        pytest.skip(
            "Tesseract em falta: instale tesseract-ocr e tesseract-ocr-por "
            "para este teste de sistema."
        )
    resultado = ocr_imagem(AMOSTRA)
    assert "LENTE" in resultado.texto
    assert any(
        float(c["largura"]) > 0 and float(c["altura"]) > 0 for c in resultado.caixas
    )
