"""Estrutura comum de página extraída: texto, spans e offsets."""

from __future__ import annotations

from dataclasses import dataclass

from engine.ingestao.caixas import Caixa


@dataclass(frozen=True)
class SpanExtraido:
    """Trecho contínuo com offsets no texto da página e caixa associada."""

    texto: str
    offset_inicio: int
    offset_fim: int
    caixa: Caixa


@dataclass(frozen=True)
class PaginaExtraida:
    """Uma página (número 1-based) com texto concatenado e spans."""

    numero: int
    texto: str
    spans: list[SpanExtraido]


__all__ = ["PaginaExtraida", "SpanExtraido"]
