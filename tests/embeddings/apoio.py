"""Doubles partilhados dos testes de embeddings (sem pesos, sem download)."""

from __future__ import annotations

import math

from engine.embeddings.carregar import (
    DIMENSAO_NATIVA,
    MODELO_ID,
    SessaoEmbedding,
    caminho_pesos,
)


class ModeloDuplo:
    """Double do EmbeddingGemma: 768d determinísticos; vision/audio nulos."""

    vision_config = None
    audio_config = None

    def encode(self, textos):
        if isinstance(textos, str):
            textos = [textos]
        return [_vector_nativo(t) for t in textos]


def _vector_nativo(texto: str) -> list[float]:
    semente = sum(ord(c) for c in texto) + len(texto) * 17
    out: list[float] = []
    for i in range(DIMENSAO_NATIVA):
        out.append(math.sin((semente + i + 1) * 0.017) * 0.1 + 0.01)
    return out


def sessao_dupla(*, dispositivo: str = "cpu", dtype: str = "float32") -> SessaoEmbedding:
    return SessaoEmbedding(
        modelo_id=MODELO_ID,
        caminho=caminho_pesos("models"),
        dispositivo=dispositivo,
        dtype=dtype,
        vision_config=None,
        audio_config=None,
        _modelo=ModeloDuplo(),
    )
