"""União de candidatos FTS ∪ embedding sem fusão RRF (PLN-09)."""

from __future__ import annotations

from dataclasses import dataclass

from engine.pesquisa.fts import HitFts
from engine.pesquisa.vec import ResultadoCosseno


@dataclass(frozen=True)
class Candidato:
    """Candidato pré-juiz; ``fontes`` regista de onde veio (fts / embedding)."""

    origem: str
    origem_id: int
    documento_id: int | None
    hash_id: int | None
    fontes: frozenset[str]
    cosseno: float | None = None
    texto: str | None = None


def unir_candidatos(
    *,
    fts: list[HitFts],
    embedding: list[ResultadoCosseno],
) -> list[Candidato]:
    """Fundir por (origem, origem_id) sem scores RRF nem limiar."""
    por_chave: dict[tuple[str, int], Candidato] = {}

    for hit in fts:
        chave = (hit.origem, hit.origem_id)
        actual = por_chave.get(chave)
        if actual is None:
            por_chave[chave] = Candidato(
                origem=hit.origem,
                origem_id=hit.origem_id,
                documento_id=hit.documento_id,
                hash_id=hit.hash_id,
                fontes=frozenset({"fts"}),
                texto=hit.texto,
            )
        else:
            por_chave[chave] = Candidato(
                origem=actual.origem,
                origem_id=actual.origem_id,
                documento_id=actual.documento_id,
                hash_id=actual.hash_id,
                fontes=actual.fontes | {"fts"},
                cosseno=actual.cosseno,
                texto=actual.texto or hit.texto,
            )

    for viz in embedding:
        chave = ("bloco", viz.bloco_id)
        actual = por_chave.get(chave)
        if actual is None:
            por_chave[chave] = Candidato(
                origem="bloco",
                origem_id=viz.bloco_id,
                documento_id=None,
                hash_id=viz.hash_id,
                fontes=frozenset({"embedding"}),
                cosseno=viz.cosseno,
            )
        else:
            por_chave[chave] = Candidato(
                origem=actual.origem,
                origem_id=actual.origem_id,
                documento_id=actual.documento_id,
                hash_id=actual.hash_id or viz.hash_id,
                fontes=actual.fontes | {"embedding"},
                cosseno=viz.cosseno,
                texto=actual.texto,
            )

    return list(por_chave.values())
