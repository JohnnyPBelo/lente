"""Extracção de ficheiros ``.txt`` (UTF-8 com fallback latin-1)."""

from __future__ import annotations

from pathlib import Path

from engine.ingestao.tipos import FicheiroInexistente

# Fallback documentado: se UTF-8 falhar, interpreta-se como latin-1
# (ISO-8859-1), que cobre qualquer sequência de bytes sem rejeitar o ficheiro
# em silêncio. Outros charsets não são detectados automaticamente.
ENCODING_PRINCIPAL = "utf-8"
ENCODING_FALLBACK = "latin-1"


def _normalizar_newlines(texto: str) -> str:
    return texto.replace("\r\n", "\n").replace("\r", "\n")


def extrair(caminho: Path | str) -> str:
    """Lê o ficheiro como texto; UTF-8 primeiro, depois latin-1."""
    destino = Path(caminho)
    if not destino.is_file():
        raise FicheiroInexistente(str(destino))
    bruto = destino.read_bytes()
    try:
        texto = bruto.decode(ENCODING_PRINCIPAL)
    except UnicodeDecodeError:
        texto = bruto.decode(ENCODING_FALLBACK)
    return _normalizar_newlines(texto)
