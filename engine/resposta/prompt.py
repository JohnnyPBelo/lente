"""Montagem do contexto do E2B: só trechos desta procura (+ página aberta)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from engine.resposta.tipos import PaginaAberta, TrechoPacote

# Instruções de prosa por lente — docs/modelos/prefixos-e-lentes.md
# Distintas dos prefixos EmbeddingGemma (task: search result / …).
INSTRUCOES_LENTE: dict[str, str] = {
    "investigar": (
        "Responde em português de Portugal. Usa só os trechos numerados desta procura.\n"
        "Cada frase afirmativa termina com a citação [n] do trecho que a sustenta.\n"
        "Não inventes controlos, datas nem cláusulas que não estejam nos trechos.\n"
        "Prefere frases curtas e ligadas à prova na página."
    ),
    "assessment": (
        "Responde em português de Portugal no registo de assessment: o que o texto afirma, "
        "o que falta, e o risco residual só se os trechos o permitirem.\n"
        "Cada afirmação termina com [n]. Sem [n], não escrevas a frase.\n"
        "Não emits parecer jurídico nem receita de ataque; resume evidência citada."
    ),
    "acreditacao": (
        "Responde em português de Portugal no registo de acreditação: requisitos, "
        "evidências e lacunas só com base nos trechos.\n"
        "Cada frase de conformidade ou não conformidade termina com [n].\n"
        "Não completes requisitos com conhecimento geral fora dos trechos."
    ),
    "verificar": (
        "Responde em português de Portugal. Trata a pergunta como verificação factual "
        "contra os trechos.\n"
        "Marca o que está suportado, o que está contradito e o que está ausente; "
        "cada afirmação com [n].\n"
        "Não suavizes contradições; cita o trecho."
    ),
    "procurar": (
        "Responde em português de Portugal com base só nos trechos numerados.\n"
        "Cada frase termina com [n]. Se os trechos não chegarem, não completes com "
        "conhecimento externo."
    ),
}


@dataclass(frozen=True)
class PacotePrompt:
    """Pacote de contexto para uma visita do E2B."""

    pergunta: str
    trechos: tuple[TrechoPacote, ...]
    instrucao: str
    pagina_aberta: PaginaAberta | None = None
    # Campos recebidos mas deliberadamente ignorados (contrato ADR-004 / FOR-006)
    _ignorados: tuple[str, ...] = field(default_factory=tuple)


def montar_contexto(
    trechos: Sequence[TrechoPacote],
    *,
    pergunta: str,
    lente: str | None = None,
    pagina_aberta: PaginaAberta | None = None,
    pergunta_sobre_pagina_aberta: bool = False,
    prosa_anterior: Sequence[str] | None = None,
    exemplos_confirmados: Sequence[str] | None = None,
    feedback_positivo: Sequence[str] | None = None,
    biblioteca_completa: Sequence[Any] | None = None,
) -> PacotePrompt:
    """Monta o pacote só com trechos aprovados (+ página aberta se aplicável).

    ``prosa_anterior``, ``exemplos_confirmados``, ``feedback_positivo`` e
    ``biblioteca_completa`` são aceites na assinatura para a API os poder
    passar — e são **ignorados** no texto do prompt.
    """
    ignorados: list[str] = []
    if prosa_anterior:
        ignorados.append("prosa_anterior")
    if exemplos_confirmados:
        ignorados.append("exemplos_confirmados")
    if feedback_positivo:
        ignorados.append("feedback_positivo")
    if biblioteca_completa:
        ignorados.append("biblioteca_completa")

    chave = (lente or "procurar").casefold()
    instrucao = INSTRUCOES_LENTE.get(chave, INSTRUCOES_LENTE["procurar"])

    pagina = pagina_aberta if pergunta_sobre_pagina_aberta else None

    return PacotePrompt(
        pergunta=pergunta,
        trechos=tuple(trechos),
        instrucao=instrucao,
        pagina_aberta=pagina,
        _ignorados=tuple(ignorados),
    )


def texto_do_prompt(pacote: PacotePrompt) -> str:
    """Serializa o pacote para o E2B. Sem prosa antiga nem few-shot."""
    linhas: list[str] = [pacote.instrucao, "", f"Pergunta: {pacote.pergunta}", ""]
    linhas.append("Trechos desta procura:")
    for t in pacote.trechos:
        pagina = f"p.{t.pagina}" if t.pagina is not None else "p.?"
        linhas.append(f"[{t.n}] {t.ficheiro} {pagina}: {t.texto}")
    if pacote.pagina_aberta is not None:
        p = pacote.pagina_aberta
        linhas.append("")
        linhas.append(
            f"Página aberta no leitor ({p.ficheiro or p.documento_id} p.{p.pagina}):"
        )
        linhas.append(p.texto)
    return "\n".join(linhas)
