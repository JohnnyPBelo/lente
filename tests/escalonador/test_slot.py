"""Regressão REG-BUS-012: procura pausa indexação/LoRA e retoma no fim."""

from __future__ import annotations

import threading
import time

import pytest

from engine.escalonador.estados import FilaOcupada
from engine.escalonador.slot import SlotPesado


def test_reg_bus_012() -> None:
    """Indexação e LoRA pausam perante procura; nunca duas procuras em paralelo."""
    slot = SlotPesado()

    # --- Indexação pausa e retoma ---
    ticks: list[str] = []
    index_entrou = threading.Event()
    index_concluiu = threading.Event()
    pode_terminar = threading.Event()

    def indexar() -> None:
        with slot.antes_de_indexar():
            index_entrou.set()
            ticks.append("index_inicio")
            while not pode_terminar.is_set():
                slot.ponto_de_pausa()
                ticks.append("index_activo")
                time.sleep(0.01)
            ticks.append("index_fim")
        index_concluiu.set()

    t_index = threading.Thread(target=indexar, name="index", daemon=True)
    t_index.start()
    assert index_entrou.wait(2.0), "indexação não arrancou"
    assert slot.estado_atual() == "index"

    with slot.antes_de_procurar():
        # adquirir só regressa depois da indexação ceder o slot
        assert slot.estado_atual() == "paused_for_search"
        assert slot.pausas_observadas >= 1
        assert slot.esta_pausado()
        activos_durante = [x for x in ticks if x == "index_activo"]
        time.sleep(0.05)
        activos_depois = [x for x in ticks if x == "index_activo"]
        assert activos_depois == activos_durante

    assert index_concluiu.wait(0.01) is False
    pode_terminar.set()
    assert index_concluiu.wait(2.0), "indexação não retomou e concluiu"
    assert ticks[-1] == "index_fim"
    assert "index_activo" in ticks
    assert slot.estado_atual() == "idle"

    # --- LoRA pausa e retoma (procura usa ONNX já activo) ---
    lora_entrou = threading.Event()
    lora_concluiu = threading.Event()
    lora_pode_terminar = threading.Event()
    onnx_visto: list[str] = []
    pausas_antes = slot.pausas_observadas

    def treinar() -> None:
        with slot.antes_de_lora():
            lora_entrou.set()
            while not lora_pode_terminar.is_set():
                slot.ponto_de_pausa()
                time.sleep(0.01)
        lora_concluiu.set()

    t_lora = threading.Thread(target=treinar, name="lora", daemon=True)
    t_lora.start()
    assert lora_entrou.wait(2.0)
    assert slot.estado_atual() == "lora"

    with slot.antes_de_procurar():
        assert slot.estado_atual() == "paused_for_search"
        assert slot.pausas_observadas > pausas_antes
        onnx_visto.append(slot.onnx_activo())
    lora_pode_terminar.set()
    assert lora_concluiu.wait(2.0), "LoRA não retomou"
    assert onnx_visto == [slot.onnx_activo()]
    assert slot.estado_atual() == "idle"

    # --- Nunca duas procuras pesadas ao mesmo tempo ---
    procura_segura = threading.Event()

    def primeira_procura() -> None:
        with slot.antes_de_procurar():
            procura_segura.set()
            time.sleep(0.1)

    t_search = threading.Thread(target=primeira_procura, name="search1", daemon=True)
    t_search.start()
    assert procura_segura.wait(2.0)
    with pytest.raises(FilaOcupada) as excinfo:
        with slot.antes_de_procurar():
            pass
    assert str(excinfo.value) == "fila ocupada"
    t_search.join(2.0)
    assert slot.estado_atual() == "idle"
