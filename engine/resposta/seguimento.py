"""Reescrita de seguimento: perguntas anteriores só completam a query."""

from __future__ import annotations


def reescrever_seguimento(pergunta_anterior: str, seguimento: str) -> str:
    """Junta o contexto do chat à pergunta curta para a pesquisa.

    A frase reescrita vai à pesquisa; não é mostrada como conhecimento
    nem entra no prompt do E2B como prosa.
    """
    ant = pergunta_anterior.strip()
    seg = seguimento.strip()
    if not ant:
        return seg
    if not seg:
        return ant
    # Seguimento típico («e o X?»): incorporar o tema anterior.
    if seg.casefold().startswith("e ") or seg.startswith("?"):
        return f"{ant.rstrip('?').rstrip()} — {seg.lstrip()}"
    return f"{ant.rstrip('?').rstrip()}; {seg}"
