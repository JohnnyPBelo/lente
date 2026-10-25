"""Regressão REG-DES-003: orçamento — um pesado; miniaturas sem re-render."""

from __future__ import annotations

import threading
import time
from pathlib import Path

from engine.escalonador import obter_miniatura
from engine.escalonador.slot import SlotPesado


def test_reg_des_003(tmp_path: Path) -> None:
    """Procura e indexação não ficam ambas activas; miniatura vem do ficheiro."""
    slot = SlotPesado()
    index_entrou = threading.Event()
    index_sair = threading.Event()

    def indexar() -> None:
        with slot.antes_de_indexar():
            index_entrou.set()
            while not index_sair.is_set():
                slot.ponto_de_pausa()
                time.sleep(0.01)

    t = threading.Thread(target=indexar, daemon=True)
    t.start()
    assert index_entrou.wait(2.0)

    with slot.antes_de_procurar():
        estado = slot.estado_atual()
        assert estado == "paused_for_search"
        # Não há indexação e procura «activas» em pleno ao mesmo tempo.
        assert estado != "index"
        assert estado != "search" or slot.esta_pausado()

    index_sair.set()
    t.join(2.0)
    assert slot.estado_atual() == "idle"

    # Miniatura gravada na indexação: o renderer de PDF espião não é chamado.
    thumb = tmp_path / "doc1_p1.webp"
    thumb.write_bytes(b"webp-fake")
    chamadas: list[object] = []

    def renderizar_pdf_espiao(*_args, **_kwargs) -> bytes:
        chamadas.append((_args, _kwargs))
        raise AssertionError("não se renderiza PDF no hover")

    dados = obter_miniatura(thumb, renderizar_pdf=renderizar_pdf_espiao)
    assert dados == b"webp-fake"
    assert chamadas == []
