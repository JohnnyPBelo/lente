"""Regressão REG-BUS-007: identificador literal fura o chão de cosseno."""

from __future__ import annotations

from typing import Sequence

from engine.pesquisa.limiar import CHAO_COSSENO_OMISSAO, filtrar_chao_cosseno
from engine.pesquisa.pipeline import Candidato, procurar


class _SessaoRejeita:
    """Juiz que rejeita tudo (scores abaixo de qualquer limiar útil)."""

    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]:
        del pergunta
        return [-10.0] * len(frases)


class _SessaoAceita:
    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]:
        del pergunta
        return [1.0] * len(frases)


def test_reg_bus_007() -> None:
    """Literal abaixo do chão mantém-se; juiz rejeitado → sem highlight forçado."""
    chao = CHAO_COSSENO_OMISSAO
    assert chao > 0

    literal = Candidato(
        id="cve",
        texto="CVE-2099-0001 afecta o módulo X.",
        cosseno=chao - 0.2,
        literal=True,
    )
    fraco = Candidato(
        id="ruido",
        texto="texto sem relação semântica",
        cosseno=chao - 0.2,
        literal=False,
    )
    forte = Candidato(
        id="sem",
        texto="módulo X e vulnerabilidade",
        cosseno=chao + 0.1,
        literal=False,
    )

    mantidos = filtrar_chao_cosseno([literal, fraco, forte], chao=chao)
    ids = {c.id for c in mantidos}
    assert "cve" in ids
    assert "sem" in ids
    assert "ruido" not in ids

    # Juiz rejeita o literal → não há highlight forçado só por FTS
    highlights = procurar(
        "CVE-2099-0001",
        ranking_fts=["cve"],
        ranking_embedding=["sem"],
        textos={
            "cve": literal.texto,
            "sem": forte.texto,
        },
        cossenos={"cve": literal.cosseno, "sem": forte.cosseno},
        literais={"cve"},
        sessao_juiz=_SessaoRejeita(),
        origem_limiar={"limiar_juiz": 0.0},
    )
    assert highlights == []

    # Com juiz a aceitar, o literal pode highlight (não é bypass do juiz)
    highlights_ok = procurar(
        "CVE-2099-0001",
        ranking_fts=["cve"],
        ranking_embedding=["sem"],
        textos={"cve": literal.texto, "sem": forte.texto},
        cossenos={"cve": literal.cosseno, "sem": forte.cosseno},
        literais={"cve"},
        sessao_juiz=_SessaoAceita(),
        origem_limiar={"limiar_juiz": 0.0},
    )
    assert any(h.id == "cve" for h in highlights_ok)
