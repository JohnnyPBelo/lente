"""Bind estrito a loopback (REG-SEG-002 / REG-HTTP-001)."""

from __future__ import annotations

HOST_OMISSAO = "127.0.0.1"
PORTA_OMISSAO = 4317

_HOSTS_RECUSADOS = frozenset(
    {
        "0.0.0.0",
        "::",
        "*",
        "",
    }
)


class BindPublicoRecusado(ValueError):
    """Configurar um host público ou wildcard é recusado."""

    def __init__(self, host: str) -> None:
        self.host = host
        super().__init__(
            f"Bind público recusado: {host!r}. Use apenas 127.0.0.1."
        )


def validar_bind(host: str, porta: int) -> None:
    """Aceita só loopback IPv4; recusa 0.0.0.0 e wildcards."""
    del porta  # a porta é livre em testes; o host é a restrição de segurança
    normalizado = (host or "").strip().lower()
    if normalizado in _HOSTS_RECUSADOS or normalizado.startswith("::"):
        raise BindPublicoRecusado(host)
    if normalizado not in {"127.0.0.1", "localhost"}:
        # Outros endereços (LAN, etc.) também ficam de fora por omissão
        raise BindPublicoRecusado(host)
