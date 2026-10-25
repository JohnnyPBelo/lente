"""Regressão REG-SEG-001: recusa de URLs privadas, loopback e esquemas inválidos."""

from __future__ import annotations

import ipaddress

import pytest

from engine.ingestao.ssrf import UrlRecusada, validar_url


def _resolver_publico(host: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    assert host == "exemplo.test"
    return [ipaddress.ip_address("203.0.113.10")]


def test_reg_seg_001() -> None:
    """Matriz SSRF: privados / file → UrlRecusada; host público mock passa; redirect privado."""
    recusados = (
        "http://127.0.0.1/x",
        "http://10.0.0.1/",
        "http://192.168.0.1/",
        "http://169.254.169.254/",
        "http://[::1]/",
        "file:///etc/passwd",
    )
    for alvo in recusados:
        with pytest.raises(UrlRecusada) as contexto:
            validar_url(alvo)
        assert contexto.value.codigo == "url_privada"

    validar_url("http://exemplo.test/artigo", resolver=_resolver_publico)

    # Redirect para IP privado: validação do destino (sem fetch ao alvo).
    with pytest.raises(UrlRecusada) as contexto_redir:
        validar_url("http://127.0.0.1/segredo")
    assert contexto_redir.value.codigo == "url_privada"
