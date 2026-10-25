"""SHA-256 dos bytes de um ficheiro (hex minúsculo)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from engine.ingestao.tipos import FicheiroInexistente

_TAMANHO_BLOCO = 1024 * 1024


def sha256_ficheiro(caminho: Path | str) -> str:
    """Calcula o SHA-256 do ficheiro, lendo em blocos.

    Devolve 64 caracteres hexadecimais minúsculos. Levanta
    ``FicheiroInexistente`` se o caminho não existir ou não for ficheiro.
    """
    destino = Path(caminho)
    if not destino.is_file():
        raise FicheiroInexistente(str(destino))
    digest = hashlib.sha256()
    with destino.open("rb") as ficheiro:
        while True:
            bloco = ficheiro.read(_TAMANHO_BLOCO)
            if not bloco:
                break
            digest.update(bloco)
    return digest.hexdigest()
