"""Fusão por Reciprocal Rank Fusion (RRF) de duas listas ordenadas.

Contrato: ``docs/modelos/fusao-limiar-platt.md`` — k de omissão 60;
empates estáveis por id.
"""

from __future__ import annotations

from typing import Hashable, Sequence, TypeVar

T = TypeVar("T", bound=Hashable)

K_OMISSAO = 60


def rrf(
    lista_a: Sequence[T],
    lista_b: Sequence[T],
    *,
    k: int = K_OMISSAO,
) -> list[T]:
    """Fundir duas rankings por RRF: score(d) = Σ 1/(k + rank_r(d)).

    Ranks são 1-based (primeiro lugar = 1). Ids ausentes numa lista
    não somam nessa lista. Empates resolvem-se pelo id (ordem estável).
    """
    if k < 0:
        raise ValueError(f"k RRF tem de ser ≥ 0, recebi {k}")

    scores: dict[T, float] = {}
    for ranking in (lista_a, lista_b):
        vistos: set[T] = set()
        for posicao, ident in enumerate(ranking, start=1):
            if ident in vistos:
                continue
            vistos.add(ident)
            scores[ident] = scores.get(ident, 0.0) + 1.0 / (k + posicao)

    return sorted(scores.keys(), key=lambda i: (-scores[i], str(i)))
