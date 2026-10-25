"""Resolução do directório ``data/`` e do ficheiro SQLite da Lente."""

from __future__ import annotations

from pathlib import Path

NOME_FICHEIRO = "lente.sqlite"
MARCADOR_RAIZ = "docs/origem/plano.md"


def raiz_projecto(partida: Path | None = None) -> Path:
    """Sobe a partir de ``partida`` (ou deste ficheiro) até à raiz do repositório."""
    aqui = (partida or Path(__file__)).resolve()
    for candidato in [aqui, *aqui.parents]:
        if (candidato / MARCADOR_RAIZ).is_file():
            return candidato
    raise RuntimeError("Não encontrei a raiz do projecto Lente.")


def pasta_dados(raiz: Path | None = None, criar: bool = True) -> Path:
    """Devolve ``data/`` sob a raiz; cria a pasta se ``criar`` for verdadeiro."""
    destino = (raiz or raiz_projecto()) / "data"
    if criar:
        destino.mkdir(parents=True, exist_ok=True)
    return destino


def caminho_sqlite(raiz: Path | None = None, criar_pasta: bool = True) -> Path:
    """Caminho canónico ``data/lente.sqlite`` (um ficheiro = o índice local)."""
    return pasta_dados(raiz=raiz, criar=criar_pasta) / NOME_FICHEIRO
