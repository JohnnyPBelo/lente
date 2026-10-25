"""Extracção de Markdown: texto + títulos para sumário preliminar."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from engine.ingestao import texto as texto_mod

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class ExtraccaoMarkdown:
    """Texto plano e lista de títulos ``{nivel, titulo}``."""

    texto: str
    titulos: list[dict[str, object]]


def _ancora(titulo: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", titulo.lower(), flags=re.UNICODE)
    slug = re.sub(r"[\s_]+", "-", slug.strip())
    return slug


def extrair(caminho: Path | str) -> ExtraccaoMarkdown:
    """Lê ``.md`` / ``.markdown`` e recolhe headings ATX."""
    corpo = texto_mod.extrair(caminho)
    titulos: list[dict[str, object]] = []
    for match in _HEADING.finditer(corpo):
        nivel = len(match.group(1))
        titulo = match.group(2).strip()
        if not titulo:
            continue
        titulos.append(
            {
                "nivel": nivel,
                "titulo": titulo,
                "ancora": _ancora(titulo),
            }
        )
    return ExtraccaoMarkdown(texto=corpo, titulos=titulos)
