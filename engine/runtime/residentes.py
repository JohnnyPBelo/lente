"""Modelos residentes numa procura (fora da janela em que o E2B escreve)."""

from __future__ import annotations

from engine.embeddings.dispositivo import DTYPE_CPU

# Identificadores estáveis para REG-MOD-009.
EMBEDDING_RESIDENTE = "EmbeddingGemma"
JUIZ_RESIDENTE = "juiz-onnx-int8"
E2B_VISITA = "E2B"


def listar_residentes(*, e2b_a_escrever: bool = False) -> list[str]:
    """EmbeddingGemma + juiz ONNX int8; o E2B nunca fica residente permanente.

    ``e2b_a_escrever`` documenta a janela de visita: mesmo aí o E2B não entra
    na lista de residentes permanentes desta API.
    """
    del e2b_a_escrever
    return [EMBEDDING_RESIDENTE, JUIZ_RESIDENTE]


def e2b_e_residente() -> bool:
    """O E2B é visita — nunca residente."""
    return False


def dtype_embedding_cpu() -> str:
    """Float32 em CPU (REG-BUS-001 / REG-MOD-009)."""
    return DTYPE_CPU
