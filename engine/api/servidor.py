"""Arranque do listener HTTP só em loopback."""

from __future__ import annotations

import socket
import threading
from typing import Any

from engine.api.bind import HOST_OMISSAO, PORTA_OMISSAO, validar_bind


class ServidorLocal:
    """Handle mínimo: endereço efectivo e paragem."""

    def __init__(
        self,
        *,
        sock: socket.socket | None = None,
        servidor: Any = None,
        thread: threading.Thread | None = None,
    ) -> None:
        self._sock = sock
        self._servidor = servidor
        self._thread = thread

    def endereco_efectivo(self) -> tuple[str, int]:
        if self._sock is not None:
            host, port, *_ = self._sock.getsockname()
            return str(host), int(port)
        if self._servidor is not None:
            servers = getattr(self._servidor, "servers", None) or []
            if servers:
                sock = servers[0].sockets[0]
                host, port, *_ = sock.getsockname()
                return str(host), int(port)
        raise RuntimeError("Servidor sem endereço efectivo")

    def parar(self) -> None:
        if self._servidor is not None:
            self._servidor.should_exit = True
            if self._thread is not None:
                self._thread.join(timeout=5)
            self._servidor = None
            self._thread = None
        if self._sock is not None:
            try:
                self._sock.close()
            finally:
                self._sock = None


def arrancar_servidor(
    *,
    host: str = HOST_OMISSAO,
    porta: int = PORTA_OMISSAO,
    app: Any = None,
) -> ServidorLocal:
    """Escuta em ``host:porta`` após validar bind; ``app`` opcional (uvicorn)."""
    validar_bind(host, porta)

    if app is None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, porta))
        sock.listen(8)
        return ServidorLocal(sock=sock)

    import uvicorn

    config = uvicorn.Config(
        app,
        host=host,
        port=porta,
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    # Espera o bind efectivo
    for _ in range(100):
        if getattr(server, "started", False) or (
            getattr(server, "servers", None)
        ):
            break
        threading.Event().wait(0.05)
    return ServidorLocal(servidor=server, thread=thread)
