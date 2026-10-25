"""Regressão REG-BUS-004: fusão RRF de FTS e embedding (k=60)."""

from __future__ import annotations

from engine.pesquisa.rrf import rrf


def test_reg_bus_004() -> None:
    """Consenso nas duas listas sobe; ids só numa ficam abaixo; sem highlight na fusão."""
    # a bem colocado em FTS e embedding; b só FTS; c só embedding
    fts = ["a", "b", "x"]
    embedding = ["a", "c", "y"]

    fundida = rrf(fts, embedding, k=60)

    assert fundida[0] == "a"
    assert fundida.index("a") < fundida.index("b")
    assert fundida.index("a") < fundida.index("c")
    assert len(fundida) == len(set(fundida))
    assert set(fundida) == {"a", "b", "c", "x", "y"}
    # A fusão devolve ids ordenados, não marcas de highlight
    assert all(isinstance(i, str) for i in fundida)
