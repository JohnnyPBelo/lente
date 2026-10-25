"""Cópia de segurança local: zip da pasta ``data/``, sem nuvem."""

from __future__ import annotations

import zipfile
from pathlib import Path


class PastaDataInexistente(FileNotFoundError):
    """A pasta de dados a copiar não existe."""


def criar_copia(pasta_data: Path | str, destino_zip: Path | str) -> Path:
    """Cria um zip com o conteúdo de ``pasta_data`` no caminho local escolhido.

    Não faz upload. O destino é um ficheiro no sistema de ficheiros local.
    """
    origem = Path(pasta_data).resolve()
    if not origem.is_dir():
        raise PastaDataInexistente(str(origem))

    destino = Path(destino_zip)
    if not destino.is_absolute():
        destino = destino.resolve()
    destino.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(destino, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for caminho in sorted(origem.rglob("*")):
            if caminho.is_file():
                arco = caminho.relative_to(origem).as_posix()
                zf.write(caminho, arcname=arco)

    return destino
