"""Orquestra visita do E2B + duas portas; degrada a excertos sem GGUF."""

from __future__ import annotations

from typing import Protocol, Sequence

from engine.resposta.e2b import EscritorE2B, PesosE2BAusentes
from engine.resposta.filtrar import ResultadoResposta, fechar_mensagem, filtrar_frases
from engine.resposta.prompt import montar_contexto, texto_do_prompt
from engine.resposta.tipos import Excerto, Miniatura, PaginaAberta, TrechoPacote

# Modos que disparam prosa (visita E2B). Alerta/lacunas/confrontar: não.
_MODOS_COM_ESCRITOR = frozenset({"procurar", "correlacionar"})


class _SessaoAvaliavel(Protocol):
    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]: ...


class _Escritor(Protocol):
    def disponivel(self) -> bool: ...

    @property
    def residente(self) -> bool: ...

    def carregar(self) -> None: ...

    def gerar(self, prompt: str) -> str: ...

    def libertar(self) -> None: ...


def modo_chama_escritor(modo: str) -> bool:
    """Alerta e lacunas não chamam o E2B; procurar/correlacionar sim."""
    return modo.casefold() in _MODOS_COM_ESCRITOR


def _partir_candidatos(prosa: str) -> list[str]:
    """Parte a prosa bruta em frases candidatas (uma por linha ou ponto final)."""
    linhas = [ln.strip() for ln in prosa.splitlines() if ln.strip()]
    if linhas:
        return linhas
    texto = prosa.strip()
    return [texto] if texto else []


def gerar_resposta(
    *,
    pergunta: str,
    trechos: Sequence[TrechoPacote],
    modo: str,
    escritor: _Escritor | EscritorE2B,
    miniaturas: Sequence[Miniatura] | None = None,
    excertos: Sequence[Excerto] | None = None,
    sessao_juiz: _SessaoAvaliavel | None = None,
    lente: str | None = None,
    pagina_aberta: PaginaAberta | None = None,
    pergunta_sobre_pagina_aberta: bool = False,
) -> ResultadoResposta:
    """Gera prosa filtrada ou degrada a excertos/miniaturas sem cair."""
    mini = list(miniaturas or [])
    exc = list(excertos or [])
    if not exc and trechos:
        exc = [
            Excerto(
                n=t.n,
                documento_id=t.documento_id,
                pagina=t.pagina,
                texto=t.texto,
                offset_inicio=t.offset_inicio,
                offset_fim=t.offset_fim,
            )
            for t in trechos
        ]

    if not modo_chama_escritor(modo):
        return fechar_mensagem(
            ResultadoResposta(
                frases=[],
                excertos=exc,
                miniaturas=mini,
            )
        )

    if not escritor.disponivel():
        # Sem GGUF: excertos + miniaturas; não propaga PesosE2BAusentes.
        return fechar_mensagem(
            ResultadoResposta(
                frases=[],
                excertos=exc,
                miniaturas=mini,
            )
        )

    pacote = montar_contexto(
        trechos,
        pergunta=pergunta,
        lente=lente,
        pagina_aberta=pagina_aberta,
        pergunta_sobre_pagina_aberta=pergunta_sobre_pagina_aberta,
    )
    prompt = texto_do_prompt(pacote)

    try:
        escritor.carregar()
        prosa = escritor.gerar(prompt)
    except PesosE2BAusentes:
        return fechar_mensagem(
            ResultadoResposta(frases=[], excertos=exc, miniaturas=mini)
        )
    finally:
        escritor.libertar()

    if sessao_juiz is None:
        # Sem juiz não há porta 2 — não emitir prosa.
        return fechar_mensagem(
            ResultadoResposta(frases=[], excertos=exc, miniaturas=mini)
        )

    candidatos = _partir_candidatos(prosa)
    filtrado = filtrar_frases(
        candidatos,
        pacote=trechos,
        sessao=sessao_juiz,
        miniaturas=mini,
        excertos=exc,
    )
    return fechar_mensagem(filtrado)
