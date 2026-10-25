"""Limites de CPU: ≥2 núcleos livres; E2B ≤ nproc−2; LoRA ≤ 2."""

from __future__ import annotations

from typing import TypedDict


class LimitesCpu(TypedDict):
    nproc: int
    livres_minimos: int
    e2b_max: int
    lora_max: int


LIVRES_MINIMOS = 2
LORA_MAX = 2


def limites_cpu(nproc: int) -> LimitesCpu:
    """Calcula o orçamento de núcleos para um ``nproc`` lógico."""
    if nproc < LIVRES_MINIMOS:
        raise ValueError(
            f"nproc={nproc} é insuficiente: são precisos pelo menos "
            f"{LIVRES_MINIMOS} núcleos livres para sistema/UI."
        )
    return {
        "nproc": nproc,
        "livres_minimos": LIVRES_MINIMOS,
        "e2b_max": nproc - LIVRES_MINIMOS,
        "lora_max": LORA_MAX,
    }
