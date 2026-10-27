"""Validação de URL contra SSRF local: só HTTP(S) público."""

from __future__ import annotations

import ipaddress
import socket
from collections.abc import Callable, Sequence
from urllib.parse import urlparse

ResolverDns = Callable[
    [str],
    Sequence[ipaddress.IPv4Address | ipaddress.IPv6Address],
]

# CGNAT / shared address space (RFC 6598) — não é ``is_private`` em todas as
# versões de Python, mas é rede de operador e deve ser recusada.
_REDE_CGNAT = ipaddress.ip_network("100.64.0.0/10")


class UrlRecusada(Exception):
    """URL fora da política de superfície (código estável ``url_privada``)."""

    def __init__(
        self,
        url: str,
        mensagem: str = "Endereço privado recusado.",
    ) -> None:
        self.url = url
        self.codigo = "url_privada"
        self.mensagem = mensagem
        super().__init__(mensagem)


def _resolver_sistema(
    host: str,
) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    encontrados: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
    vistos: set[str] = set()
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror as erro:
        raise UrlRecusada(host, "Endereço privado recusado.") from erro
    for info in infos:
        sockaddr = info[4]
        if not sockaddr:
            continue
        texto = sockaddr[0]
        if texto in vistos:
            continue
        vistos.add(texto)
        encontrados.append(ipaddress.ip_address(texto))
    return encontrados


def _ip_recusado(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        return _ip_recusado(ip.ipv4_mapped)
    if isinstance(ip, ipaddress.IPv4Address) and ip in _REDE_CGNAT:
        return True
    if isinstance(ip, ipaddress.IPv6Address):
        # IPv4-compatible / mapped já tratado; CGNAT só aplica a IPv4.
        pass
    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def validar_url(
    url: str,
    *,
    resolver: ResolverDns | None = None,
) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    """Recusa esquemas não HTTP(S), credenciais e hosts/IPs privados.

    Devolve a lista de IPs públicos validados (pin para o fetch).
    ``resolver`` permite injectar DNS nos testes; por omissão usa o sistema.
    """
    analisado = urlparse(url)
    esquema = (analisado.scheme or "").lower()
    if esquema not in {"http", "https"}:
        raise UrlRecusada(url)
    if analisado.username is not None or analisado.password is not None:
        raise UrlRecusada(url)
    host = analisado.hostname
    if not host:
        raise UrlRecusada(url)

    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None

    if literal is not None:
        if _ip_recusado(literal):
            raise UrlRecusada(url)
        return [literal]

    resolver_efectivo = resolver or _resolver_sistema
    enderecos = list(resolver_efectivo(host))
    if not enderecos:
        raise UrlRecusada(url)
    if any(_ip_recusado(ip) for ip in enderecos):
        raise UrlRecusada(url)
    return list(enderecos)
