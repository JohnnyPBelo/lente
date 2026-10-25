"""Pesquisa: FTS/embedding (PLN-07), fusão RRF, limiar e Platt (PLN-09)."""

from __future__ import annotations

from engine.pesquisa.feedback_runtime import (
    CorrecaoRecente,
    material_para_escritor,
    reordenar_por_feedback,
)
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

__all__ = [
    "CHAO_COSSENO_OMISSAO",
    "CorrecaoRecente",
    "EscalaPlatt",
    "Highlight",
    "K_OMISSAO",
    "MINIMO_CORRECOES",
    "TAU_BRUTO_OMISSAO",
    "TAU_PLATT_OMISSAO",
    "calibrar",
    "filtrar_chao_cosseno",
    "filtrar_por_limiar",
    "identidade",
    "limiar_visivel",
    "ler_limiar",
    "material_para_escritor",
    "procurar",
    "reordenar_por_feedback",
    "rrf",
    "texto_query_com_prefixo",
]
