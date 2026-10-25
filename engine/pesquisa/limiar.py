"""Limiar visível do juiz e chão de cosseno (literais furam o chão).

Contrato: ``docs/modelos/fusao-limiar-platt.md``, ADR-014.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence, TypeVar

# Score bruto ONNX: passa se s ≥ τ₀
TAU_BRUTO_OMISSAO = 0.0
# Após Platt: passa se p ≥ 0,50
TAU_PLATT_OMISSAO = 0.5
# Chão semântico habitual antes do juiz (literais furam)
CHAO_COSSENO_OMISSAO = 0.30

T = TypeVar("T")


@dataclass(frozen=True)
class EstadoLimiar:
    """Valor numérico legível do limiar em vigor."""

    valor: float
    platt_activo: bool


_estado = EstadoLimiar(valor=TAU_BRUTO_OMISSAO, platt_activo=False)


def limiar_visivel() -> float:
    """Número em vigor (visível na API / estado de aprendizagem)."""
    return _estado.valor


def estado_limiar() -> EstadoLimiar:
    return _estado


def definir_limiar(valor: float, *, platt_activo: bool | None = None) -> EstadoLimiar:
    """Actualiza o limiar em memória (fonte para UI/API)."""
    global _estado
    activo = _estado.platt_activo if platt_activo is None else platt_activo
    _estado = EstadoLimiar(valor=float(valor), platt_activo=activo)
    return _estado


def limiar_por_omissao(*, platt_activo: bool) -> float:
    return TAU_PLATT_OMISSAO if platt_activo else TAU_BRUTO_OMISSAO


def ler_limiar(
    origem: Mapping[str, float] | None = None,
    *,
    platt_activo: bool | None = None,
) -> float:
    """Lê o limiar de config/mapa (BD) ou cai no default documentado.

    ``origem`` pode ser um dict com a chave ``limiar_juiz`` (ex. preferências
    lidas da BD). Sem chave, usa o estado em memória ou o default.
    """
    activo = _estado.platt_activo if platt_activo is None else platt_activo
    if origem is not None and "limiar_juiz" in origem:
        valor = float(origem["limiar_juiz"])
        definir_limiar(valor, platt_activo=activo)
        return valor
    if platt_activo is not None and platt_activo != _estado.platt_activo:
        valor = limiar_por_omissao(platt_activo=activo)
        definir_limiar(valor, platt_activo=activo)
        return valor
    return _estado.valor


def filtrar_por_limiar(
    pontuados: Sequence[tuple[T, float]],
    *,
    tau: float | None = None,
) -> list[T]:
    """Mantém ids com score ≥ τ. Lista vazia se nada passa."""
    corte = limiar_visivel() if tau is None else float(tau)
    return [ident for ident, score in pontuados if score >= corte]


class _CandidatoCosseno(Protocol):
    id: object
    cosseno: float
    literal: bool


def filtrar_chao_cosseno(
    candidatos: Sequence[_CandidatoCosseno],
    *,
    chao: float = CHAO_COSSENO_OMISSAO,
) -> list[_CandidatoCosseno]:
    """Antes do juiz: descarta cosseno baixo, excepto identificador literal."""
    mantidos: list[_CandidatoCosseno] = []
    for c in candidatos:
        if c.literal or c.cosseno >= chao:
            mantidos.append(c)
    return mantidos
