"""Mutex do slot pesado: um trabalho de cada vez; a procura preempta."""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from typing import Literal

from engine.escalonador.estados import Estado, FilaOcupada

TipoPesado = Literal["search", "index", "lora"]
TipoPausavel = Literal["index", "lora"]


class SlotPesado:
    """Garante um trabalho pesado de cada vez.

    A procura pausa indexação e LoRA e retoma-os no fim. Um segundo pedido
    pesado que não seja essa preempção levanta ``FilaOcupada``.
    """

    def __init__(self, *, onnx_activo: str = "onnx_activo") -> None:
        self._cv = threading.Condition()
        self._activo: TipoPesado | None = None
        self._pausado: TipoPausavel | None = None
        self._quer_pausa = False
        self._onnx_activo = onnx_activo
        self.pausas_observadas = 0

    def estado_atual(self) -> str:
        with self._cv:
            if self._activo == "search" and self._pausado is not None:
                return Estado.PAUSED_FOR_SEARCH.value
            if self._activo is None:
                return Estado.IDLE.value
            return self._activo

    def esta_pausado(self) -> bool:
        with self._cv:
            return self._pausado is not None or (
                self._quer_pausa and self._activo in ("index", "lora")
            )

    def onnx_activo(self) -> str:
        """ONNX do juiz em vigor; a procura usa-o mesmo com LoRA pausado."""
        return self._onnx_activo

    def ponto_de_pausa(self) -> None:
        """Ponto de cooperação: indexação/LoRA cedem o slot à procura."""
        with self._cv:
            if self._activo not in ("index", "lora") and self._pausado is None:
                return
            while True:
                if self._quer_pausa and self._activo in ("index", "lora"):
                    self._pausado = self._activo  # type: ignore[assignment]
                    self._activo = None
                    self.pausas_observadas += 1
                    self._cv.notify_all()
                if self._pausado is not None and self._activo != self._pausado:
                    self._cv.wait()
                    continue
                return

    def _entrar(self, tipo: TipoPesado) -> None:
        with self._cv:
            if tipo == "search":
                if self._activo == "search":
                    raise FilaOcupada()
                if self._activo in ("index", "lora"):
                    self._quer_pausa = True
                    self._cv.notify_all()
                    while self._activo in ("index", "lora"):
                        self._cv.wait()
                self._activo = "search"
                self._cv.notify_all()
                return

            if self._activo is not None or self._pausado is not None:
                raise FilaOcupada()
            self._activo = tipo
            self._cv.notify_all()

    def _sair(self, tipo: TipoPesado) -> None:
        with self._cv:
            if tipo == "search":
                if self._activo == "search":
                    self._activo = None
                self._quer_pausa = False
                if self._pausado is not None:
                    self._activo = self._pausado
                    self._pausado = None
                self._cv.notify_all()
                return

            if self._activo == tipo:
                self._activo = None
            if self._pausado == tipo:
                self._pausado = None
            self._cv.notify_all()

    @contextmanager
    def adquirir(self, tipo: TipoPesado) -> Iterator[SlotPesado]:
        self._entrar(tipo)
        try:
            yield self
        finally:
            self._sair(tipo)

    def antes_de_procurar(self) -> AbstractContextManager[SlotPesado]:
        return self.adquirir("search")

    def antes_de_indexar(self) -> AbstractContextManager[SlotPesado]:
        return self.adquirir("index")

    def antes_de_lora(self) -> AbstractContextManager[SlotPesado]:
        return self.adquirir("lora")


def gravar_feedback_imediato(
    destino: dict[str, object],
    entrada: dict[str, object],
    *,
    slot: SlotPesado | None = None,
) -> None:
    """Feedback leve: grava em disco/memória sem adquirir o slot pesado."""
    del slot  # explícito: não se usa o slot
    destino.clear()
    destino.update(entrada)
