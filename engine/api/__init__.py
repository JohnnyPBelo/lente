"""API HTTP local da Lente (127.0.0.1:4317)."""

from __future__ import annotations

from engine.api.bind import HOST_OMISSAO, PORTA_OMISSAO, BindPublicoRecusado, validar_bind

__all__ = [
    "HOST_OMISSAO",
    "PORTA_OMISSAO",
    "BindPublicoRecusado",
    "criar_app",
    "validar_bind",
]


def __getattr__(nome: str):
    if nome == "criar_app":
        from engine.api.app import criar_app

        return criar_app
    raise AttributeError(nome)
