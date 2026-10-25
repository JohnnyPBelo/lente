"""Regressões do pacote de contexto do E2B (sem prosa anterior nem exemplos)."""

from __future__ import annotations

from engine.resposta.prompt import montar_contexto, texto_do_prompt
from engine.resposta.tipos import PaginaAberta, TrechoPacote


def _trechos() -> list[TrechoPacote]:
    return [
        TrechoPacote(
            n=1,
            ficheiro="a.pdf",
            pagina=1,
            texto="Cláusula A exige registo.",
            documento_id="doc_a",
        ),
        TrechoPacote(
            n=2,
            ficheiro="b.pdf",
            pagina=2,
            texto="Cláusula B exige revisão anual.",
            documento_id="doc_b",
        ),
    ]


def test_reg_res_001() -> None:
    """Pacote traz ficheiro, página e texto dos trechos aprovados — não a biblioteca."""
    trechos = _trechos()
    pacote = montar_contexto(
        trechos,
        pergunta="O que exige a cláusula A?",
        biblioteca_completa=[
            {"ficheiro": "z.pdf", "texto": "Documento que não passou o juiz."}
        ],
    )

    assert len(pacote.trechos) == 2
    assert pacote.trechos[0].ficheiro == "a.pdf"
    assert pacote.trechos[0].pagina == 1
    assert "Cláusula A" in pacote.trechos[0].texto
    assert pacote.trechos[1].ficheiro == "b.pdf"
    texto = texto_do_prompt(pacote)
    assert "Documento que não passou o juiz" not in texto
    assert "biblioteca" not in texto.casefold() or "Cláusula A" in texto


def test_reg_res_002() -> None:
    """Prosa anterior do assistente não entra no prompt."""
    pacote = montar_contexto(
        _trechos(),
        pergunta="E a cláusula B?",
        prosa_anterior=[
            "Resposta antiga inventada com [1].",
            "Outra prosa do assistente.",
        ],
    )
    texto = texto_do_prompt(pacote)
    assert "Resposta antiga inventada" not in texto
    assert "Outra prosa do assistente" not in texto


def test_reg_res_003() -> None:
    """Página aberta no leitor entra além dos trechos aprovados."""
    pagina = PaginaAberta(
        documento_id="doc_a",
        pagina=1,
        texto="Texto completo da página aberta no leitor, para além do excerto.",
        ficheiro="a.pdf",
    )
    pacote = montar_contexto(
        _trechos(),
        pergunta="O que diz esta página sobre a cláusula A?",
        pagina_aberta=pagina,
        pergunta_sobre_pagina_aberta=True,
    )
    texto = texto_do_prompt(pacote)
    assert "Texto completo da página aberta" in texto
    assert "Cláusula A exige registo" in texto


def test_reg_for_006() -> None:
    """Histórico de respostas e feedback positivo não entram como few-shot."""
    pacote = montar_contexto(
        _trechos(),
        pergunta="O que exige a cláusula?",
        prosa_anterior=["Exemplo confirmado de prosa. [1]"],
        exemplos_confirmados=[
            "Pergunta antiga → Resposta confirmada com polegar. [1]"
        ],
        feedback_positivo=["Trecho bom confirmado pelo utilizador."],
    )
    texto = texto_do_prompt(pacote)
    assert "Exemplo confirmado de prosa" not in texto
    assert "Resposta confirmada com polegar" not in texto
    assert "Trecho bom confirmado" not in texto
    assert "few-shot" not in texto.casefold()
