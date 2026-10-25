"""Regressão REG-SEG-002: bind só em 127.0.0.1; porto de serviço 4317."""

from __future__ import annotations

import socket

import pytest

from engine.api.bind import (
    HOST_OMISSAO,
    PORTA_OMISSAO,
    BindPublicoRecusado,
    validar_bind,
)
from engine.api.servidor import arrancar_servidor


def _porto_livre_loopback() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def test_reg_seg_002() -> None:
    """Por omissão o host é 127.0.0.1 e o porto 4317; 0.0.0.0 falha."""
    assert HOST_OMISSAO == "127.0.0.1"
    assert PORTA_OMISSAO == 4317

    with pytest.raises(BindPublicoRecusado):
        validar_bind("0.0.0.0", 4317)

    with pytest.raises(BindPublicoRecusado):
        validar_bind("::", 4317)

    porto = _porto_livre_loopback()
    validar_bind("127.0.0.1", porto)

    servidor = arrancar_servidor(host="127.0.0.1", porta=porto, app=None)
    try:
        host, port = servidor.endereco_efectivo()
        assert host == "127.0.0.1"
        assert port == porto
        assert host != "0.0.0.0"
    finally:
        servidor.parar()
