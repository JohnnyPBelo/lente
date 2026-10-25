"""PNG / JPEG / WebP → raster utilizável pelo OCR.

Sem Pillow no caminho crítico: o Tesseract (Leptonica) lê estes formatos
directamente. ``gravar_raster_rgb`` escreve PNG mínimo (stdlib) para testes.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

from engine.ingestao.tipos import FicheiroInexistente, TipoNaoSuportado

_EXTENSOES = {
    ".png": "png",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".webp": "webp",
}


def classificar_imagem(caminho: Path | str) -> str:
    """Devolve ``png``, ``jpeg`` ou ``webp``; caso contrário ``TipoNaoSuportado``."""
    destino = Path(caminho)
    extensao = destino.suffix.lower()
    tipo = _EXTENSOES.get(extensao)
    if tipo is None:
        raise TipoNaoSuportado(str(destino), extensao)
    return tipo


def raster_para_ocr(caminho: Path | str) -> Path:
    """Valida existência e tipo; devolve o caminho absoluto para o Tesseract."""
    destino = Path(caminho)
    if not destino.is_file():
        raise FicheiroInexistente(str(destino))
    classificar_imagem(destino)
    return destino.resolve()


def gravar_raster_rgb(
    caminho: Path | str,
    *,
    largura: int,
    altura: int,
    cor: tuple[int, int, int] = (255, 255, 255),
) -> Path:
    """Escreve um PNG RGB sintético (sem dependências externas)."""
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    r, g, b = cor
    linha = bytes((0, *[c for _ in range(largura) for c in (r, g, b)]))
    raw = linha * altura
    comprimido = zlib.compress(raw, 9)

    def _chunk(tipo: bytes, dados: bytes) -> bytes:
        return (
            struct.pack(">I", len(dados))
            + tipo
            + dados
            + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", largura, altura, 8, 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", comprimido)
        + _chunk(b"IEND", b"")
    )
    destino.write_bytes(png)
    return destino
