"""Privilegio imediato a trechos confirmados/rejeitados entre candidatos.

Não injecta texto de feedback no escritor (E2B). Só reordena ids já
recuperados quando a pergunta é muito parecida com a da correcção.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class CorrecaoRecente:
    """Par etiquetado recente (sem prosa para o escritor)."""

    pergunta: str
    trecho_id: str
    positivo: bool


def perguntas_parecidas(a: str, b: str, *, limiar: float = 0.5) -> bool:
    """Sobreposição de tokens casefold — stub leve até haver embedding de query."""
    ta = set(a.casefold().split())
    tb = set(b.casefold().split())
    if not ta or not tb:
        return False
    inter = len(ta & tb)
    uniao = len(ta | tb)
    return (inter / uniao) >= limiar


def reordenar_por_feedback(
    candidatos: Sequence[str],
    *,
    pergunta: str,
    correcoes: Sequence[CorrecaoRecente],
) -> list[str]:
    """Confirmados sobem e rejeitados descem, só entre ``candidatos``.

    Correções de perguntas pouco parecidas são ignoradas. Não acrescenta
    ids que a pesquisa não trouxe.
    """
    ids = list(candidatos)
    conjunto = set(ids)
    boost: set[str] = set()
    penalizacao: set[str] = set()

    for c in correcoes:
        if c.trecho_id not in conjunto:
            continue
        if not perguntas_parecidas(pergunta, c.pergunta):
            continue
        if c.positivo:
            boost.add(c.trecho_id)
        else:
            penalizacao.add(c.trecho_id)

    def chave(ident: str) -> tuple[int, int]:
        # Menor chave = mais cedo: boost (-1), neutro (0), penalizado (1)
        if ident in boost:
            return (0, ids.index(ident))
        if ident in penalizacao:
            return (2, ids.index(ident))
        return (1, ids.index(ident))

    return sorted(ids, key=chave)


def material_para_escritor(
    correcoes: Sequence[CorrecaoRecente],
) -> list[str]:
    """O escritor não recebe texto de feedback como exemplos.

    Devolve sempre lista vazia: o contrato proíbe injectar «respostas
    correctas» no prompt do E2B.
    """
    del correcoes  # explícito: correções não entram no material
    return []
