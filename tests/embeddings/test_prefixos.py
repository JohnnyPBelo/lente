"""Regressão REG-BUS-002: prefixos de documento e de query por lente."""

from __future__ import annotations

from engine.embeddings.prefixos import prefixo_documento, prefixo_query


def test_reg_bus_002() -> None:
    """Documento title|text; lentes → question answering / fact checking / search."""
    doc = prefixo_documento("Relatorio sintetico", "conteudo do bloco")
    assert doc.startswith("title: Relatorio sintetico | text: ")
    assert doc.endswith("conteudo do bloco")

    sem_titulo = prefixo_documento(None, "so texto")
    assert sem_titulo.startswith("title: none | text: ")

    pergunta = "Qual e o controlo de acesso remoto?"
    for lente in ("investigar", "acreditacao"):
        q = prefixo_query(pergunta, lente=lente)
        assert q.startswith("task: question answering | query: ")
        assert q.endswith(pergunta)

    for lente in ("verificar", "assessment"):
        q = prefixo_query(pergunta, lente=lente)
        assert q.startswith("task: fact checking | query: ")
        assert q.endswith(pergunta)

    curta = prefixo_query(pergunta, lente=None)
    assert curta.startswith("task: search result | query: ")
    assert curta.endswith(pergunta)
