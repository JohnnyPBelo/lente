"""Escala de Platt sobre scores do juiz.

Só activa com ≥ ``MINIMO_CORRECOES`` pares etiquetados únicos.
Abaixo disso a escala é a identidade (score bruto).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Sequence

# Contrato: docs/modelos/fusao-limiar-platt.md
MINIMO_CORRECOES = 50

Escala = Callable[[float], float]


def identidade(score: float) -> float:
    """Sem Platt: devolve o score bruto."""
    return float(score)


@dataclass(frozen=True)
class EscalaPlatt:
    """p = σ(a · s + b)."""

    a: float
    b: float

    def __call__(self, score: float) -> float:
        return _sigmoide(self.a * float(score) + self.b)

    @property
    def activa(self) -> bool:
        return True


def _sigmoide(x: float) -> float:
    # Estável numericamente
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def calibrar(
    pares: Sequence[tuple[float, int]],
) -> Escala:
    """Ajusta (a, b) se houver correções suficientes; senão identidade.

    ``pares``: (score_bruto, etiqueta) com etiqueta 1 (positivo) ou 0 (negativo).
    Pares duplicados contam uma vez (unicidade por (score, etiqueta) arredondado).
    """
    unicos = _pares_unicos(pares)
    if len(unicos) < MINIMO_CORRECOES:
        return identidade

    a, b = _ajustar_platt(unicos)
    return EscalaPlatt(a=a, b=b)


def _pares_unicos(
    pares: Sequence[tuple[float, int]],
) -> list[tuple[float, float]]:
    vistos: set[tuple[float, int]] = set()
    saida: list[tuple[float, float]] = []
    for score, etiqueta in pares:
        et = 1 if int(etiqueta) else 0
        chave = (round(float(score), 6), et)
        if chave in vistos:
            continue
        vistos.add(chave)
        # Alvo de Platt com suavização clássica (evitar 0/1 exactos)
        saida.append((float(score), float(et)))
    return saida


def _ajustar_platt(
    pares: Sequence[tuple[float, float]],
    *,
    iteracoes: int = 100,
) -> tuple[float, float]:
    """Regressão logística 1D (Newton) com alvos suavizados de Platt."""
    n = len(pares)
    n_pos = sum(1 for _, y in pares if y >= 0.5)
    n_neg = n - n_pos
    # Alvos de Platt (1999): (n_pos+1)/(n_pos+2) e 1/(n_neg+2)
    t_pos = (n_pos + 1.0) / (n_pos + 2.0) if n_pos else 0.5
    t_neg = 1.0 / (n_neg + 2.0) if n_neg else 0.5

    alvos = [t_pos if y >= 0.5 else t_neg for _, y in pares]
    scores = [s for s, _ in pares]

    a = 0.0
    b = math.log((n_pos + 1e-3) / (n_neg + 1e-3))

    for _ in range(iteracoes):
        grad_a = 0.0
        grad_b = 0.0
        hess_aa = 0.0
        hess_ab = 0.0
        hess_bb = 0.0
        for s, t in zip(scores, alvos):
            p = _sigmoide(a * s + b)
            d = p - t
            w = p * (1.0 - p)
            grad_a += d * s
            grad_b += d
            hess_aa += w * s * s
            hess_ab += w * s
            hess_bb += w

        det = hess_aa * hess_bb - hess_ab * hess_ab
        if abs(det) < 1e-12:
            break
        da = (hess_bb * grad_a - hess_ab * grad_b) / det
        db = (hess_aa * grad_b - hess_ab * grad_a) / det
        a -= da
        b -= db
        if abs(da) + abs(db) < 1e-8:
            break

    # Garantir monotonicidade crescente tipicamente útil (scores altos → p alto)
    if a < 0:
        a = -a
        b = -b
    return a, b
