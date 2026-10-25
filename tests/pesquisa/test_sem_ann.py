"""Regressão REG-FOR-001: sem base vectorial externa nem ANN."""

from __future__ import annotations

import ast
from pathlib import Path

import engine.pesquisa as pacote_pesquisa
from engine.pesquisa.vec import tipo_indice


def _ficheiros_pesquisa() -> list[Path]:
    raiz = Path(pacote_pesquisa.__file__).resolve().parent
    return sorted(p for p in raiz.glob("*.py") if p.is_file())


def test_reg_for_001() -> None:
    """Inventário: sem Qdrant/Chroma/LanceDB/Postgres/ANN; índice exacto no SQLite."""
    assert tipo_indice() == "exacto"

    proibidos = {
        "qdrant",
        "qdrant_client",
        "chromadb",
        "chroma",
        "lancedb",
        "psycopg",
        "psycopg2",
        "postgres",
        "pgvector",
        "faiss",
        "hnswlib",
        "annoy",
    }

    for ficheiro in _ficheiros_pesquisa():
        fonte = ficheiro.read_text(encoding="utf-8")
        arvore = ast.parse(fonte, filename=str(ficheiro))
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                for alias in no.names:
                    raiz = alias.name.split(".", 1)[0].casefold()
                    assert raiz not in proibidos, f"import {alias.name} em {ficheiro.name}"
            elif isinstance(no, ast.ImportFrom) and no.module:
                raiz = no.module.split(".", 1)[0].casefold()
                assert raiz not in proibidos, f"from {no.module} em {ficheiro.name}"
