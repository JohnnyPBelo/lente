"""Feedback do juiz: registo de pares e LoRA quando a máquina está livre."""

from __future__ import annotations

from engine.feedback.exportar_onnx import exportar_onnx_atomico
from engine.feedback.lora import (
    LEARNING_RATE,
    RANK,
    EstadoTorch,
    libertar_torch,
    treinar_lora,
)
from engine.feedback.registar import (
    ajustar_pontuacoes,
    hash_par,
    listar_pares,
    registar_acertou,
    registar_corrigir,
    registar_descartar,
)
from engine.feedback.validar_troca import avaliar_holdout

__all__ = [
    "LEARNING_RATE",
    "RANK",
    "EstadoTorch",
    "ajustar_pontuacoes",
    "avaliar_holdout",
    "exportar_onnx_atomico",
    "hash_par",
    "libertar_torch",
    "listar_pares",
    "registar_acertou",
    "registar_corrigir",
    "registar_descartar",
    "treinar_lora",
]
