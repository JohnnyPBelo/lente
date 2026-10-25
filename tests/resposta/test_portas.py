"""Regressões das duas portas: citação [n] e fidelidade do juiz."""

from __future__ import annotations

from typing import Sequence

from engine.pesquisa.limiar import TAU_BRUTO_OMISSAO, definir_limiar
from engine.resposta.filtrar import ResultadoParcial, filtrar_frases, fechar_mensagem
from engine.resposta.porta1_citacao import passar_porta1
from engine.resposta.porta2_fiel import passar_porta2
from engine.resposta.tipos import Excerto, Miniatura, TrechoPacote


class _JuizDupla:
    """Double do juiz: score alto só se a frase contém uma âncora do trecho."""

    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]:
        del pergunta
        scores: list[float] = []
        for frase in frases:
            # «contradiz» / inventado → baixo; overlap com trecho → alto
            if "contradiz" in frase.casefold() or "marciano" in frase.casefold():
                scores.append(-1.0)
            else:
                scores.append(1.0)
        return scores


def _pacote_um() -> list[TrechoPacote]:
    return [
        TrechoPacote(
            n=1,
            ficheiro="politica.pdf",
            pagina=3,
            texto="O acesso remoto exige aprovação do responsável de segurança.",
            documento_id="doc_1",
            offset_inicio=10,
            offset_fim=70,
        )
    ]


def test_reg_res_004() -> None:
    """Sem [n] ou [99] fora do pacote saem; [1] do pacote segue para a porta 2."""
    pacote = _pacote_um()
    sem_citacao = "O acesso remoto exige aprovação."
    fora = "Há uma regra inventada. [99]"
    valida = "O acesso remoto exige aprovação do responsável de segurança. [1]"

    assert passar_porta1(sem_citacao, pacote) is None
    assert passar_porta1(fora, pacote) is None
    aceite = passar_porta1(valida, pacote)
    assert aceite is not None
    assert aceite.n == 1
    assert aceite.texto == valida


def test_reg_res_005() -> None:
    """Frase com [1] infiel sai na porta 2; frase fiel com [1] sobrevive."""
    definir_limiar(TAU_BRUTO_OMISSAO, platt_activo=False)
    pacote = _pacote_um()
    juiz = _JuizDupla()

    infiel = "O acesso remoto é livre para qualquer marciano. [1]"
    fiel = "O acesso remoto exige aprovação do responsável de segurança. [1]"

    cand_infiel = passar_porta1(infiel, pacote)
    cand_fiel = passar_porta1(fiel, pacote)
    assert cand_infiel is not None
    assert cand_fiel is not None

    assert passar_porta2(cand_infiel, pacote, sessao=juiz) is None
    sobrevivente = passar_porta2(cand_fiel, pacote, sessao=juiz)
    assert sobrevivente is not None
    assert sobrevivente.texto == fiel
    assert sobrevivente.n == 1


def test_reg_res_006() -> None:
    """Com miniaturas visíveis e portas por concluir, não há prosa provisória."""
    pacote = _pacote_um()
    miniaturas = [
        Miniatura(documento_id="doc_1", pagina=3, caminho="thumbs/doc_1_p3.webp")
    ]
    excertos = [
        Excerto(
            n=1,
            documento_id="doc_1",
            pagina=3,
            texto=pacote[0].texto,
            offset_inicio=10,
            offset_fim=70,
        )
    ]
    candidatos = [
        "Frase provisória sem citação.",
        "O acesso remoto exige aprovação do responsável de segurança. [1]",
    ]

    parcial = ResultadoParcial(
        miniaturas=miniaturas,
        excertos=excertos,
        candidatos_brutos=candidatos,
        portas_concluidas=False,
    )
    assert parcial.frases == []
    assert parcial.prosa_provisoria is False
    assert len(parcial.miniaturas) == 1

    final = filtrar_frases(
        candidatos,
        pacote=pacote,
        sessao=_JuizDupla(),
        miniaturas=miniaturas,
        excertos=excertos,
    )
    assert final.portas_concluidas is True
    assert final.prosa_provisoria is False
    assert len(final.frases) == 1
    assert final.frases[0].n == 1
    assert all("[1]" in f.texto for f in final.frases)


def test_reg_res_007() -> None:
    """Todas rejeitadas → excertos/miniaturas sem prosa; sem trechos → aviso vazio."""
    definir_limiar(TAU_BRUTO_OMISSAO, platt_activo=False)
    pacote = _pacote_um()
    miniaturas = [Miniatura(documento_id="doc_1", pagina=3)]
    excertos = [
        Excerto(n=1, documento_id="doc_1", pagina=3, texto=pacote[0].texto)
    ]
    rejeitadas = [
        "Sem citação nenhuma.",
        "Afirmação que contradiz o trecho. [1]",
        "Fora do pacote. [99]",
    ]

    com_trechos = filtrar_frases(
        rejeitadas,
        pacote=pacote,
        sessao=_JuizDupla(),
        miniaturas=miniaturas,
        excertos=excertos,
    )
    fechado = fechar_mensagem(com_trechos)
    assert fechado.frases == []
    assert fechado.vazio is False
    assert len(fechado.excertos) >= 1
    assert len(fechado.miniaturas) >= 1
    assert fechado.aviso_vazio is None

    sem_nada = fechar_mensagem(
        filtrar_frases(
            [],
            pacote=[],
            sessao=_JuizDupla(),
            miniaturas=[],
            excertos=[],
        )
    )
    assert sem_nada.frases == []
    assert sem_nada.excertos == []
    assert sem_nada.miniaturas == []
    assert sem_nada.vazio is True
    assert sem_nada.aviso_vazio is not None
