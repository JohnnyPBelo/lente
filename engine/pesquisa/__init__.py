"""Pesquisa: FTS5 e cosseno exacto (PLN-07); fusão RRF, limiar e Platt (PLN-09)."""

from __future__ import annotations

from engine.pesquisa.candidatos import unir_candidatos
from engine.pesquisa.feedback_runtime import (
    CorrecaoRecente,
    material_para_escritor,
    reordenar_por_feedback,
)
from engine.pesquisa.fts import HitFts, apagar_fts_hash, indexar_bloco, indexar_frase, procurar_fts
from engine.pesquisa.limiar import (
    CHAO_COSSENO_OMISSAO,
    TAU_BRUTO_OMISSAO,
    TAU_PLATT_OMISSAO,
    filtrar_chao_cosseno,
    filtrar_por_limiar,
    limiar_visivel,
    ler_limiar,
)
from engine.pesquisa.pipeline import Highlight, procurar, texto_query_com_prefixo
from engine.pesquisa.platt import MINIMO_CORRECOES, EscalaPlatt, calibrar, identidade
from engine.pesquisa.rrf import K_OMISSAO, rrf
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
    "CHAO_COSSENO_OMISSAO",
    "CorrecaoRecente",
    "DIMENSOES",
    "EscalaPlatt",
    "Highlight",
    "HitFts",
    "K_OMISSAO",
    "MINIMO_CORRECOES",
    "ResultadoCosseno",
    "TAU_BRUTO_OMISSAO",
    "TAU_PLATT_OMISSAO",
    "apagar_fts_hash",
    "apagar_vectores_hash",
    "calibrar",
    "carregar_extensao",
    "filtrar_chao_cosseno",
    "filtrar_por_limiar",
    "guardar_vector",
    "identidade",
    "indexar_bloco",
    "indexar_frase",
    "limiar_visivel",
    "ler_limiar",
    "material_para_escritor",
    "normalizar",
    "procurar",
    "procurar_cosseno",
    "procurar_fts",
    "reordenar_por_feedback",
    "rrf",
    "texto_query_com_prefixo",
    "tipo_indice",
    "unir_candidatos",
]
