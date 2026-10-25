"""Pipeline de procura: candidatos → RRF → juiz → filtro limiar.

Prefixos de query por lente são stubs até PLN-14 ligar a barra
(REG-BUS-002 já fixa as strings no PLN-06).
Highlights só depois do juiz deixar passar o limiar.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from engine.pesquisa.feedback_runtime import (
    CorrecaoRecente,
    reordenar_por_feedback,
)
from engine.pesquisa.limiar import (
    CHAO_COSSENO_OMISSAO,
    filtrar_chao_cosseno,
    filtrar_por_limiar,
    ler_limiar,
)
from engine.pesquisa.platt import Escala, EscalaPlatt, identidade
from engine.pesquisa.rrf import K_OMISSAO, rrf

# Prefixos EmbeddingGemma 2 (contrato MOD-lentes) — stubs até PLN-14
PREFIXOS_QUERY = {
    "procurar": "task: search result | query: ",
    "investigar": "task: question answering | query: ",
    "acreditacao": "task: question answering | query: ",
    "verificar": "task: fact checking | query: ",
    "assessment": "task: fact checking | query: ",
}


@dataclass(frozen=True)
class Candidato:
    """Trecho candidato antes do juiz."""

    id: str
    texto: str
    cosseno: float = 1.0
    literal: bool = False


@dataclass(frozen=True)
class Highlight:
    """Trecho que passou juiz + limiar (prova para o escritor)."""

    id: str
    texto: str
    score: float


class _SessaoJuiz(Protocol):
    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]: ...


def prefixo_query(lente: str | None) -> str:
    """Prefixo EmbeddingGemma para a query conforme a lente activa."""
    if not lente:
        return PREFIXOS_QUERY["procurar"]
    return PREFIXOS_QUERY.get(lente, PREFIXOS_QUERY["procurar"])


def texto_query_com_prefixo(pergunta: str, *, lente: str | None = None) -> str:
    return f"{prefixo_query(lente)}{pergunta}"


def procurar(
    pergunta: str,
    *,
    ranking_fts: Sequence[str],
    ranking_embedding: Sequence[str],
    textos: dict[str, str],
    sessao_juiz: _SessaoJuiz,
    cossenos: dict[str, float] | None = None,
    literais: set[str] | None = None,
    lente: str | None = None,
    escala: Escala | None = None,
    correcoes: Sequence[CorrecaoRecente] | None = None,
    k_rrf: int = K_OMISSAO,
    chao_cosseno: float = CHAO_COSSENO_OMISSAO,
    origem_limiar: dict[str, float] | None = None,
) -> list[Highlight]:
    """Candidatos → chão (literais furam) → RRF → feedback → juiz → limiar.

    Devolve lista vazia se nada passar o limiar (aviso de vazio fica na API).
    """
    del lente  # prefixo entra na recuperação; aqui as listas já vêm prontas
    escala_efectiva: Escala = identidade if escala is None else escala
    activo = isinstance(escala_efectiva, EscalaPlatt)
    tau = ler_limiar(origem_limiar, platt_activo=activo)

    literais_set = literais or set()
    cossenos_map = dict(cossenos or {})

    candidatos = [
        Candidato(
            id=i,
            texto=textos.get(i, ""),
            cosseno=float(cossenos_map.get(i, 1.0)),
            literal=i in literais_set,
        )
        for i in dict.fromkeys([*ranking_fts, *ranking_embedding])
    ]
    apos_chao = filtrar_chao_cosseno(candidatos, chao=chao_cosseno)
    ids_apos_chao = {c.id for c in apos_chao}

    fts_f = [i for i in ranking_fts if i in ids_apos_chao]
    emb_f = [i for i in ranking_embedding if i in ids_apos_chao]
    fundida = rrf(fts_f, emb_f, k=k_rrf)

    if correcoes:
        fundida = reordenar_por_feedback(
            fundida, pergunta=pergunta, correcoes=correcoes
        )

    if not fundida:
        return []

    frases = [textos.get(i, "") for i in fundida]
    brutos = sessao_juiz.avaliar(pergunta, frases)
    if len(brutos) != len(fundida):
        raise ValueError("O juiz devolveu um número de scores inesperado")

    pontuados = [
        (ident, float(escala_efectiva(s)))
        for ident, s in zip(fundida, brutos)
    ]
    passam = filtrar_por_limiar(pontuados, tau=tau)
    por_id = dict(pontuados)
    return [
        Highlight(id=i, texto=textos.get(i, ""), score=por_id[i])
        for i in passam
    ]
