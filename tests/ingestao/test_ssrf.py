"""Regressão REG-SEG-001: recusa de URLs privadas, loopback e esquemas inválidos."""

from __future__ import annotations

import ipaddress
from unittest.mock import MagicMock

import pytest

from engine.ingestao.ssrf import UrlRecusada, validar_url
from engine.ingestao.url import RespostaHttp, obter_texto_url


def _resolver_publico(host: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    assert host == "exemplo.test"
    return [ipaddress.ip_address("8.8.8.8")]


def test_reg_seg_001() -> None:
    """Matriz SSRF: privados / file / redirect → UrlRecusada; host público mock passa."""
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

    transporte = MagicMock(
        side_effect=AssertionError("não deve haver fetch para alvos recusados")
    )
    for alvo in recusados:
        with pytest.raises(UrlRecusada):
            obter_texto_url(alvo, transporte=transporte)
    transporte.assert_not_called()

    chamadas: list[str] = []

    def transporte_redirect(url: str) -> RespostaHttp:
        chamadas.append(url)
        if url.rstrip("/") == "http://exemplo.test/origem":
            return RespostaHttp(
                estado=302,
                corpo=b"",
                cabecalhos={"Location": "http://127.0.0.1/segredo"},
                url=url,
            )
        raise AssertionError(f"fetch inesperado para {url!r}")

    with pytest.raises(UrlRecusada):
        obter_texto_url(
            "http://exemplo.test/origem",
            resolver=_resolver_publico,
            transporte=transporte_redirect,
        )
    assert chamadas == ["http://exemplo.test/origem"]
    assert all("127.0.0.1" not in c for c in chamadas)
