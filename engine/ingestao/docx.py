"""Extracção de ``.docx`` via OOXML (stdlib: zipfile + ElementTree).

Sem ``python-docx``: o CI só instala pytest; o plano admite declarar a
biblioteca quando existir ``pyproject.toml``.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from engine.ingestao.tipos import FicheiroInexistente

_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
_DOCUMENTO = "word/document.xml"


def _texto_paragrafo(paragrafo: ET.Element) -> str:
    partes: list[str] = []
    for no in paragrafo.iter():
        tag = no.tag.rsplit("}", 1)[-1]
        if tag == "t" and no.text:
            partes.append(no.text)
        elif tag == "tab":
            partes.append("\t")
        elif tag in {"br", "cr"}:
            partes.append("\n")
    return "".join(partes)


def extrair(caminho: Path | str) -> str:
    """Texto plano por parágrafo, na ordem do documento, newlines ``\\n``."""
    destino = Path(caminho)
    if not destino.is_file():
        raise FicheiroInexistente(str(destino))
    try:
        with zipfile.ZipFile(destino) as arquivo:
            with arquivo.open(_DOCUMENTO) as xml:
                raiz = ET.parse(xml).getroot()
    except (zipfile.BadZipFile, KeyError) as erro:
        raise ValueError(f"docx inválido: {destino}") from erro

    paragrafos: list[str] = []
    for paragrafo in raiz.findall(".//w:p", _NS):
        linha = _texto_paragrafo(paragrafo)
        if linha:
            paragrafos.append(linha)
    return "\n".join(paragrafos)
