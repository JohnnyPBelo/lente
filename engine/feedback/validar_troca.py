"""Gate de troca: rejeitar LoRA se o holdout piorar."""

from __future__ import annotations


def avaliar_holdout(metrica_base: float, metrica_nova: float) -> bool:
    """Aceita a troca só se a métrica de holdout não piorar."""
    return metrica_nova >= metrica_base
