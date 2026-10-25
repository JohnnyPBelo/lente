"""Pesquisa lexical (FTS5) e semântica (cosseno exacto 256-d) no mesmo SQLite."""

from __future__ import annotations

from engine.pesquisa.candidatos import Candidato, unir_candidatos
from engine.pesquisa.fts import HitFts, apagar_fts_hash, indexar_bloco, indexar_frase, procurar_fts
from engine.pesquisa.vec import (
    DIMENSOES,
    ResultadoCosseno,
    apagar_vectores_hash,
    carregar_extensao,
    guardar_vector,
    normalizar,
    procurar_cosseno,
    tipo_indice,
)

__all__ = [
    "DIMENSOES",
    "Candidato",
    "HitFts",
    "ResultadoCosseno",
    "apagar_fts_hash",
    "apagar_vectores_hash",
    "carregar_extensao",
    "guardar_vector",
    "indexar_bloco",
    "indexar_frase",
    "normalizar",
    "procurar_cosseno",
    "procurar_fts",
    "tipo_indice",
    "unir_candidatos",
]
