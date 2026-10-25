"""Ingestão: transformar bytes locais em texto e metadados mínimos.

PDF, OCR e URL ficam noutros planos; aqui só texto, Markdown, docx e SHA-256.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from engine.ingestao import docx as docx_mod
from engine.ingestao import markdown as markdown_mod
from engine.ingestao import texto as texto_mod
from engine.ingestao.tipos import FicheiroInexistente, TipoNaoSuportado, classificar


@dataclass(frozen=True)
class Extraccao:
    """Resultado unificado da extracção por tipo de ficheiro."""

    texto: str
    titulos: list[dict[str, object]]
    tipo: str


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
    raise TipoNaoSuportado(str(destino), destino.suffix.lower())


__all__ = [
    "Extraccao",
    "FicheiroInexistente",
    "TipoNaoSuportado",
    "classificar",
    "extrair",
]
