"""Segmentação de frases com offsets e caixas herdadas da ingestão."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from engine.ingestao.caixas import Caixa

# Fim de frase: ponto / interrogação / exclamação seguidos de espaço ou fim.
_FIM_FRASE = re.compile(r"(?<=[.!?])(?:\s+|$)")


@dataclass(frozen=True)
class FraseSegmentada:
    """Unidade de highlight/juízo: offsets no texto e caixas opcionais."""

    texto: str
    offset_inicio: int
    offset_fim: int
    ordem: int
    pagina: int | None = None
    caixas: list[Caixa] = field(default_factory=list)


def segmentar_frases(
    texto: str,
    *,
    offset_base: int = 0,
    caixas_por_intervalo: list[tuple[int, int, list[Caixa]]] | None = None,
) -> list[FraseSegmentada]:
    """Parte ``texto`` em frases; associa caixas cujo intervalo intersecta a frase.

    ``caixas_por_intervalo`` usa offsets relativos a ``texto`` (não ao documento
    inteiro). ``offset_base`` desloca os offsets gravados para o documento.
    """
    if not texto:
        return []

    frases: list[FraseSegmentada] = []
    cursor = 0
    ordem = 0
    for fim_rel in _limites_frases(texto):
        trecho = texto[cursor:fim_rel]
        # Inclui espaços finais no intervalo mas o texto da frase é stripado
        # só nas pontas internas vazias — mantém o literal do intervalo.
        literal = trecho
        if not literal.strip():
            cursor = fim_rel
            continue
        # Ajusta para não incluir só whitespace à direita no texto gravado,
        # mas os offsets cobrem o intervalo consumido até ao próximo início.
        fim_literal = cursor + len(literal.rstrip())
        inicio_literal = cursor + (len(literal) - len(literal.lstrip()))
        corpo = texto[inicio_literal:fim_literal]
        caixas = _caixas_para(
            inicio_literal,
            fim_literal,
            caixas_por_intervalo or [],
        )
        pagina = caixas[0].pagina if caixas else None
        frases.append(
            FraseSegmentada(
                texto=corpo,
                offset_inicio=offset_base + inicio_literal,
                offset_fim=offset_base + fim_literal,
                ordem=ordem,
                pagina=pagina,
                caixas=list(caixas),
            )
        )
        ordem += 1
        cursor = fim_rel

    if cursor < len(texto) and texto[cursor:].strip():
        resto = texto[cursor:]
        inicio_literal = cursor + (len(resto) - len(resto.lstrip()))
        fim_literal = cursor + len(resto.rstrip())
        corpo = texto[inicio_literal:fim_literal]
        caixas = _caixas_para(
            inicio_literal,
            fim_literal,
            caixas_por_intervalo or [],
        )
        pagina = caixas[0].pagina if caixas else None
        frases.append(
            FraseSegmentada(
                texto=corpo,
                offset_inicio=offset_base + inicio_literal,
                offset_fim=offset_base + fim_literal,
                ordem=ordem,
                pagina=pagina,
                caixas=list(caixas),
            )
        )

    return frases


def _limites_frases(texto: str) -> list[int]:
    """Devolve índices exclusive de fim de cada frase detectada."""
    limites: list[int] = []
    for m in _FIM_FRASE.finditer(texto):
        limites.append(m.end())
    return limites


def _caixas_para(
    inicio: int,
    fim: int,
    intervalos: list[tuple[int, int, list[Caixa]]],
) -> list[Caixa]:
    saida: list[Caixa] = []
    for i0, i1, caixas in intervalos:
        if i1 <= inicio or i0 >= fim:
            continue
        saida.extend(caixas)
    return saida


__all__ = ["FraseSegmentada", "segmentar_frases"]
