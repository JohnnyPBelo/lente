"""Regressão REG-BUS-010: limiar visível, Platt e highlights vazios."""

from __future__ import annotations

from typing import Sequence

from engine.pesquisa.limiar import (
    TAU_BRUTO_OMISSAO,
    TAU_PLATT_OMISSAO,
    definir_limiar,
    filtrar_por_limiar,
    limiar_visivel,
    ler_limiar,
)
from engine.pesquisa.pipeline import procurar
from engine.pesquisa.platt import (
    MINIMO_CORRECOES,
    EscalaPlatt,
    calibrar,
    identidade,
)


class _SessaoFixa:
    def __init__(self, scores: Sequence[float]) -> None:
        self._scores = list(scores)

    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]:
        del pergunta
        assert len(frases) == len(self._scores)
        return list(self._scores)


def test_reg_bus_010() -> None:
    """Platt com ≥50; identidade abaixo; nada acima do limiar → highlights vazios."""
    definir_limiar(TAU_BRUTO_OMISSAO, platt_activo=False)
    assert limiar_visivel() == TAU_BRUTO_OMISSAO
    assert ler_limiar({"limiar_juiz": 0.25}) == 0.25
    assert limiar_visivel() == 0.25

    # Abaixo do mínimo: identidade
    poucos = [(float(i), 1 if i % 2 == 0 else 0) for i in range(10)]
    escala_pouca = calibrar(poucos)
    assert escala_pouca is identidade or escala_pouca(0.0) == identidade(0.0)
    assert escala_pouca(1.5) == 1.5

    # Acima do mínimo: Platt monótona na fixture
    assert MINIMO_CORRECOES == 50
    muitos: list[tuple[float, int]] = []
    for i in range(MINIMO_CORRECOES):
        # scores baixos → negativo; altos → positivo
        if i < 25:
            muitos.append((-2.0 - i * 0.01, 0))
        else:
            muitos.append((2.0 + (i - 25) * 0.01, 1))
    escala = calibrar(muitos)
    assert isinstance(escala, EscalaPlatt)
    amostra = [-3.0, -1.0, 0.0, 1.0, 3.0]
    probs = [escala(s) for s in amostra]
    assert all(0.0 <= p <= 1.0 for p in probs)
    assert probs == sorted(probs)  # monótona crescente

    definir_limiar(TAU_PLATT_OMISSAO, platt_activo=True)
    assert limiar_visivel() == TAU_PLATT_OMISSAO

    # Procura sem nada acima do limiar → lista vazia de highlights
    definir_limiar(0.9, platt_activo=False)
    highlights = procurar(
        "o que é X?",
        ranking_fts=["t1"],
        ranking_embedding=["t1"],
        textos={"t1": "texto irrelevante"},
        sessao_juiz=_SessaoFixa([0.1]),
        escala=identidade,
    )
    assert highlights == []
    assert filtrar_por_limiar([("t1", 0.1)], tau=0.9) == []
