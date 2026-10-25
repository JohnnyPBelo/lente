"""Regressão REG-FOR-005: único decisor aceite é o mmarco deste plano."""

from __future__ import annotations

import pytest

from engine.juiz.caminhos import MODELO_ID
from engine.juiz.carregar import (
    DecisorRecusado,
    identificador_aceite,
    validar_modelo_id,
)


def test_reg_for_005() -> None:
    """Sem cliente Jev nem substituição; só o mmarco ONNX int8."""
    assert identificador_aceite() == MODELO_ID
    assert identificador_aceite() == "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"

    validar_modelo_id(MODELO_ID)

    for impostor in (
        "jev-1.14.0",
        "Jev",
        "Qwen/Qwen2.5-3B",
        "microsoft/deberta-v3-large",
        "cross-encoder/ms-marco-MiniLM-L-12-v2",
    ):
        with pytest.raises(DecisorRecusado):
            validar_modelo_id(impostor)

    import engine.juiz as pacote_juiz
    import engine.juiz.carregar as mod

    exportados = set(getattr(pacote_juiz, "__all__", []))
    assert "cliente_jev" not in exportados
    assert "Jev" not in dir(mod)
    assert not hasattr(mod, "cliente_jev")
    assert not hasattr(mod, "carregar_jev")
