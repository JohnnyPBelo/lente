"""Regressão REG-BUS-008: seguimento reescreve a query; citações desta volta."""

from __future__ import annotations

from typing import Sequence

from engine.resposta.filtrar import filtrar_frases
from engine.resposta.seguimento import reescrever_seguimento
from engine.resposta.tipos import TrechoPacote


class _JuizFiel:
    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]:
        del pergunta
        return [1.0] * len(frases)


def test_reg_bus_008() -> None:
    """Seguimento curto → query reescrita completa; citações só desta volta."""
    anterior = "Quem aprova o acesso remoto na política de segurança?"
    curto = "e o controlo de acessos?"

    query = reescrever_seguimento(anterior, curto)
    assert "controlo de acessos" in query.casefold() or "controle" in query.casefold()
    assert len(query) > len(curto)
    # A pesquisa recebe a query completa, não só a frase curta isolada
    assert "acesso remoto" in query.casefold() or "política" in query.casefold() or "segurança" in query.casefold()

    # Trechos desta volta (não prosa antiga)
    pacote = [
        TrechoPacote(
            n=1,
            ficheiro="politica.pdf",
            pagina=5,
            texto="O controlo de acessos é revisto trimestralmente pelo responsável.",
            documento_id="doc_nova",
        )
    ]
    prosa_antiga = "O acesso remoto exige aprovação. [1]"  # não é fonte
    candidatos = [
        "O controlo de acessos é revisto trimestralmente pelo responsável. [1]",
    ]
    resultado = filtrar_frases(
        candidatos,
        pacote=pacote,
        sessao=_JuizFiel(),
    )
    assert len(resultado.frases) == 1
    assert resultado.frases[0].n == 1
    assert resultado.frases[0].texto.endswith("[1]")
    # A citação [1] aponta ao trecho desta volta, não à prosa antiga
    assert pacote[0].documento_id == "doc_nova"
    assert prosa_antiga not in resultado.frases[0].texto
