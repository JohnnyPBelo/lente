"""Estados observáveis do escalonador e erro de fila ocupada."""

from __future__ import annotations

from enum import Enum


class Estado(str, Enum):
    """Estados de telemetria do slot pesado."""

    IDLE = "idle"
    SEARCH = "search"
    INDEX = "index"
    LORA = "lora"
    PAUSED_FOR_SEARCH = "paused_for_search"


ESTADOS_OBSERVAVEIS: frozenset[str] = frozenset(e.value for e in Estado)

MENSAGEM_FILA_OCUPADA = "fila ocupada"


class FilaOcupada(Exception):
    """O slot pesado está ocupado e o pedido não é uma procura a preemptir."""

    def __init__(self, mensagem: str = MENSAGEM_FILA_OCUPADA) -> None:
        self.mensagem = mensagem
        super().__init__(mensagem)
