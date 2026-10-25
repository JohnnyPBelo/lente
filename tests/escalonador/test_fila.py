"""Regressão REG-ING-009: fila de indexação um documento de cada vez."""

from __future__ import annotations

from engine.escalonador.fila_ingestao import FilaIngestao


def test_reg_ing_009() -> None:
    """Com dois documentos na fila, só um fica activo; o seguinte após concluir."""
    fila = FilaIngestao()
    fila.enfileirar("doc-a")
    fila.enfileirar("doc-b")

    primeiro = fila.proximo()
    assert primeiro == "doc-a"
    assert fila.activo == "doc-a"
    assert fila.pendentes() == ("doc-b",)

    # Enquanto o actual não termina, o seguinte não começa.
    assert fila.proximo() is None
    assert fila.activo == "doc-a"

    fila.concluir("doc-a")
    assert fila.activo is None

    segundo = fila.proximo()
    assert segundo == "doc-b"
    assert fila.activo == "doc-b"
    assert fila.pendentes() == ()
    fila.concluir("doc-b")
    assert fila.activo is None
    assert fila.proximo() is None
