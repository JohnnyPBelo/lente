"""Teto de alertas (máximo dez no total)."""

from __future__ import annotations

MAX_ALERTAS = 10


class LimiteAlertas(Exception):
    """Criação recusada: já existem dez alertas.

    O contrato HTTP mapeia para ``limite_alertas``.
    """

    codigo = "limite_alertas"
    mensagem = "Máximo de dez alertas."

    def __init__(self, mensagem: str | None = None) -> None:
        super().__init__(mensagem or self.mensagem)
        self.mensagem = mensagem or LimiteAlertas.mensagem
