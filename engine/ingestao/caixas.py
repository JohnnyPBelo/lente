"""Modelo de caixas bounding-box e serialização JSON para ``frases.caixas_json``.

Cada caixa usa o sistema de coordenadas do PDF: origem no canto inferior
esquerdo da página, unidades em pontos (1/72 polegadas), eixos crescentes
para a direita (x) e para cima (y).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Caixa:
    """Rectângulo de highlight: ``{pagina, x, y, largura, altura}``."""

    pagina: int
    x: float
    y: float
    largura: float
    altura: float

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


def caixas_para_json(caixas: list[Caixa]) -> str:
    """Serializa a lista no formato gravado em ``frases.caixas_json``."""
    return json.dumps([c.para_dict() for c in caixas], ensure_ascii=False)


def caixas_de_json(texto: str) -> list[Caixa]:
    """Lê o JSON de caixas; lista vazia se ``texto`` for vazio."""
    if not texto or not texto.strip():
        return []
    bruto = json.loads(texto)
    if not isinstance(bruto, list):
        raise ValueError("caixas_json tem de ser um array JSON")
    saida: list[Caixa] = []
    for item in bruto:
        saida.append(
            Caixa(
                pagina=int(item["pagina"]),
                x=float(item["x"]),
                y=float(item["y"]),
                largura=float(item["largura"]),
                altura=float(item["altura"]),
            )
        )
    return saida


__all__ = ["Caixa", "caixas_de_json", "caixas_para_json"]
