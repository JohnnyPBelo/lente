"""OCR de PDF quando a extracção nativa marca ``precisa_ocr``.

Não substitui ``pdf.py`` (PLN-03): só lê a bandeira e, se necessário,
rasteriza páginas (via callback injectável) e chama ``ocr_imagem``.
Quando ``precisa_ocr`` é falso, devolve o texto já extraído e não invoca
o Tesseract.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from engine.ingestao import ocr as ocr_mod
from engine.ingestao.ocr import ResultadoOCR


RenderPaginas = Callable[[Path], Sequence[Path]]


def ocr_pdf_quando_preciso(
    caminho: Path | str,
    *,
    precisa_ocr: bool,
    texto_existente: str = "",
    renderizar_paginas: RenderPaginas | None = None,
    idioma: str = "por",
    timeout: float = 60.0,
) -> ResultadoOCR:
    """Se já há texto seleccionável, devolve-o; senão OCR página a página."""
    if not precisa_ocr:
        return ResultadoOCR(
            texto=texto_existente,
            caixas=[],
            estado="ok",
        )

    destino = Path(caminho)
    if renderizar_paginas is None:
        raise ValueError(
            "PDF com precisa_ocr=True exige renderizar_paginas "
            "(raster por página); a extracção nativa fica no PLN-03."
        )

    textos: list[str] = []
    caixas: list[dict[str, float | int]] = []
    for indice, raster in enumerate(renderizar_paginas(destino), start=1):
        pagina = ocr_mod.ocr_imagem(
            raster,
            pagina=indice,
            idioma=idioma,
            timeout=timeout,
        )
        if pagina.texto:
            textos.append(pagina.texto)
        caixas.extend(pagina.caixas)

    texto = "\n".join(textos).strip()
    estado = "ok" if texto else "aviso"
    return ResultadoOCR(texto=texto, caixas=caixas, estado=estado)


__all__ = ["ocr_pdf_quando_preciso"]
