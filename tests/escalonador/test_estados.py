"""Regressão REG-MOD-004: estados observáveis e fila ocupada."""

from __future__ import annotations

import threading
import time

import pytest

from engine.escalonador.estados import ESTADOS_OBSERVAVEIS, FilaOcupada
from engine.escalonador.slot import SlotPesado, gravar_feedback_imediato


def test_reg_mod_004() -> None:
    """Segundo pesado sem preempção → fila ocupada; feedback não pede slot."""
    assert ESTADOS_OBSERVAVEIS == {
        "idle",
        "search",
        "index",
        "lora",
        "paused_for_search",
    }

    slot = SlotPesado()
    assert slot.estado_atual() == "idle"

    index_seguro = threading.Event()
    index_sair = threading.Event()

    def indexar() -> None:
        with slot.antes_de_indexar():
            index_seguro.set()
            index_sair.wait(2.0)

    t = threading.Thread(target=indexar, daemon=True)
    t.start()
    assert index_seguro.wait(2.0)
    assert slot.estado_atual() == "index"

    with pytest.raises(FilaOcupada) as excinfo:
        with slot.antes_de_lora():
            pass
    assert str(excinfo.value) == "fila ocupada"

    # Feedback imediato não adquire o slot de procura.
    estado_antes = slot.estado_atual()
    destino: dict[str, object] = {}
    gravar_feedback_imediato(
        destino,
        {"acertou": True, "par": "q|t"},
        slot=slot,
    )
    assert destino == {"acertou": True, "par": "q|t"}
    assert slot.estado_atual() == estado_antes == "index"

    index_sair.set()
    t.join(2.0)
    assert slot.estado_atual() == "idle"

    with slot.antes_de_procurar():
        assert slot.estado_atual() == "search"
        with pytest.raises(FilaOcupada):
            with slot.antes_de_indexar():
                pass

    # LoRA ≤ 2 núcleos fica no cálculo de nucleos; aqui o estado lora é observável.
    with slot.antes_de_lora():
        assert slot.estado_atual() == "lora"
        time.sleep(0.01)
