"""Embeddings EmbeddingGemma 2: blocos, frases e vectores 256d (só texto)."""

from __future__ import annotations

from engine.embeddings.carregar import (
    CONFIG_TEXTO_ONLY,
    DIMENSAO,
    DIMENSAO_NATIVA,
    MODELO_ID,
    PesosEmbeddingAusentes,
    SessaoEmbedding,
    caminho_pesos,
    carregar_modelo,
    embutir,
    pasta_embedding,
)
from engine.embeddings.cortar import (
    MARGEM_TOKENS,
    OVERLAP_TOKENS,
    TOKENS_BLOCO,
    BlocoCortado,
    cortar_blocos,
)
from engine.embeddings.dispositivo import (
    DTYPE_CPU,
    DTYPE_GPU,
    DTYPE_PROIBIDO,
    DtypeProibido,
    dtype_para,
    escolher_dispositivo,
    fluxo_unico,
    validar_dtype,
)
from engine.embeddings.frases import FraseSegmentada, segmentar_frases
from engine.embeddings.indexar import (
    ResultadoIndexacao,
    gerar_miniatura,
    guardar_vector,
    indexar_documento,
    obter_miniatura_indexada,
)
from engine.embeddings.prefixos import prefixo_documento, prefixo_query

__all__ = [
    "CONFIG_TEXTO_ONLY",
    "DIMENSAO",
    "DIMENSAO_NATIVA",
    "DTYPE_CPU",
    "DTYPE_GPU",
    "DTYPE_PROIBIDO",
    "MARGEM_TOKENS",
    "MODELO_ID",
    "OVERLAP_TOKENS",
    "TOKENS_BLOCO",
    "BlocoCortado",
    "DtypeProibido",
    "FraseSegmentada",
    "PesosEmbeddingAusentes",
    "ResultadoIndexacao",
    "SessaoEmbedding",
    "caminho_pesos",
    "carregar_modelo",
    "cortar_blocos",
    "dtype_para",
    "embutir",
    "escolher_dispositivo",
    "fluxo_unico",
    "gerar_miniatura",
    "guardar_vector",
    "indexar_documento",
    "obter_miniatura_indexada",
    "pasta_embedding",
    "prefixo_documento",
    "prefixo_query",
    "segmentar_frases",
    "validar_dtype",
]
