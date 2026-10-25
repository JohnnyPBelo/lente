"""Regressão REG-BUS-001: vector 256d, L2≈1, float32, sem NaN, sem float16."""

from __future__ import annotations

import math

import pytest

from engine.embeddings.carregar import (
    CONFIG_TEXTO_ONLY,
    DIMENSAO,
    SessaoEmbedding,
    embutir,
)
from engine.embeddings.dispositivo import (
    DTYPE_CPU,
    DTYPE_PROIBIDO,
    DtypeProibido,
    validar_dtype,
)


def test_reg_bus_001(sessao_embedding: SessaoEmbedding) -> None:
    """Frase sintética em CPU → 256d, norma ~1, float32, sem NaN; sem float16."""
    sessao = sessao_embedding
    assert sessao.dtype == DTYPE_CPU
    assert sessao.dtype != DTYPE_PROIBIDO
    assert sessao.vision_config is None
    assert sessao.audio_config is None
    assert CONFIG_TEXTO_ONLY == {"vision_config": None, "audio_config": None}

    frase = "A frase sintetica do embedding corre em float32 na CPU."
    vector = embutir(frase, sessao=sessao)

    assert len(vector) == DIMENSAO
    assert all(isinstance(x, float) for x in vector)
    assert all(not math.isnan(x) for x in vector)
    norma = math.sqrt(sum(x * x for x in vector))
    assert abs(norma - 1.0) < 1e-5

    with pytest.raises(DtypeProibido):
        validar_dtype("float16")
    with pytest.raises(DtypeProibido):
        validar_dtype("fp16")
    assert sessao.dtype == "float32"
