"""Regressão REG-MOD-006: só GGUF Q4 de visita; BF16 de treino recusado."""

from __future__ import annotations

import pytest

from engine.resposta.e2b import (
    ARTEFACTO_GGUF_Q4,
    MODELO_HF_ID,
    ArtefactoRecusado,
    artefactos_aceites,
    validar_artefacto,
)


def test_reg_mod_006() -> None:
    """Carregador aceita só o GGUF Q4; recusa o pacote BF16 ~11 GB. Sem download."""
    aceites = artefactos_aceites()
    assert len(aceites) == 1
    assert aceites[0] == ARTEFACTO_GGUF_Q4
    assert "q4" in aceites[0].casefold()
    assert MODELO_HF_ID == "google/gemma-4-E2B-it-qat-q4_0-gguf"

    assert validar_artefacto(ARTEFACTO_GGUF_Q4) == ARTEFACTO_GGUF_Q4
    assert validar_artefacto("gemma-4-E2B-it-qat-q4_0.gguf") == ARTEFACTO_GGUF_Q4

    for nome in (
        "gemma-4-E2B-it-bf16",
        "gemma-4-E2B-it.safetensors",
        "pytorch_model-00001-of-00005.bin",
        "model-bf16.gguf",
        "unquantized-11gb",
    ):
        with pytest.raises(ArtefactoRecusado):
            validar_artefacto(nome)
