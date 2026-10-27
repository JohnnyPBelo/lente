"""Ingestão: transformar bytes locais em texto e metadados mínimos."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from engine.ingestao import docx as docx_mod
from engine.ingestao import markdown as markdown_mod
from engine.ingestao import texto as texto_mod
from engine.ingestao.paginas import PaginaExtraida
from engine.ingestao.tipos import FicheiroInexistente, TipoNaoSuportado, classificar


@dataclass(frozen=True)
class Extraccao:
    """Resultado unificado da extracção por tipo de ficheiro."""

    texto: str
    titulos: list[dict[str, object]]
    tipo: str
    paginas: list[PaginaExtraida] | None = None
    caixas: list[dict[str, float | int]] | None = None
    precisa_ocr: bool | None = None


def extrair(caminho: Path | str) -> Extraccao:
    """Extrai texto (e títulos, se Markdown) conforme a extensão."""
    destino = Path(caminho)
    if not destino.is_file():
        raise FicheiroInexistente(str(destino))
    tipo = classificar(destino)
    if tipo == "texto":
        return Extraccao(texto=texto_mod.extrair(destino), titulos=[], tipo=tipo)
    if tipo == "markdown":
        md = markdown_mod.extrair(destino)
        return Extraccao(texto=md.texto, titulos=list(md.titulos), tipo=tipo)
    if tipo == "docx":
        return Extraccao(texto=docx_mod.extrair(destino), titulos=[], tipo=tipo)
    if tipo == "pdf":
        from engine.ingestao import pdf as pdf_mod

        pdf = pdf_mod.extrair_pdf(destino)
        return Extraccao(
            texto=pdf.texto,
            titulos=[],
            tipo=tipo,
            paginas=list(pdf.paginas),
            precisa_ocr=pdf.precisa_ocr,
        )
    if tipo == "imagem":
        from engine.ingestao import ocr as ocr_mod

        ocr = ocr_mod.ocr_imagem(destino)
        return Extraccao(
            texto=ocr.texto,
            titulos=[],
            tipo=tipo,
            caixas=list(ocr.caixas),
        )
    raise TipoNaoSuportado(str(destino), destino.suffix.lower())


__all__ = [
    "Extraccao",
    "FicheiroInexistente",
    "TipoNaoSuportado",
    "classificar",
    "extrair",
]
