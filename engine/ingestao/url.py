"""Ingestão por URL HTTP(S): fetch pontual, extracção de texto, registo."""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import HTTPRedirectHandler, Request, build_opener

from engine.ingestao.registo import DocumentoRegisto, registar_texto
from engine.ingestao.ssrf import ResolverDns, UrlRecusada, validar_url

USER_AGENT = "Lente"
TIMEOUT_S = 20
LIMITE_BYTES = 2_000_000
MAX_REDIRECTS = 5


class _SemRedirect(HTTPRedirectHandler):
    """Impede o urllib de seguir redirects — a revalidação SSRF fica em ``obter_texto_url``."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        del req, fp, code, msg, headers, newurl
        return None


@dataclass(frozen=True)
class RespostaHttp:
    """Resposta HTTP mínima para transporte injectável nos testes."""

    estado: int
    corpo: bytes
    cabecalhos: dict[str, str]
    url: str


Transporte = Callable[[str], RespostaHttp]


class _ExtratorTexto(HTMLParser):
    """Extrai texto visível; ignora script, style e nos semelhantes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignorar = 0
        self._partes: list[str] = []
        self.titulo = ""
        self._em_titulo = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        nome = tag.lower()
        if nome in {"script", "style", "noscript", "svg", "template"}:
            self._ignorar += 1
            return
        if nome == "title" and self._ignorar == 0:
            self._em_titulo = True
        if nome in {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self._partes.append("\n")

    def handle_endtag(self, tag: str) -> None:
        nome = tag.lower()
        if nome in {"script", "style", "noscript", "svg", "template"}:
            self._ignorar = max(0, self._ignorar - 1)
            return
        if nome == "title":
            self._em_titulo = False

    def handle_data(self, data: str) -> None:
        if self._ignorar:
            return
        if self._em_titulo:
            self.titulo += data
            return
        self._partes.append(data)

    def texto(self) -> str:
        bruto = "".join(self._partes)
        linhas = [re.sub(r"[ \t]+", " ", linha).strip() for linha in bruto.splitlines()]
        return "\n".join(linha for linha in linhas if linha)


def _cabecalhos_mapa(brutos: object) -> dict[str, str]:
    mapa: dict[str, str] = {}
    if brutos is None:
        return mapa
    items = getattr(brutos, "items", None)
    if callable(items):
        for chave, valor in items():
            mapa[str(chave)] = str(valor)
        return mapa
    if isinstance(brutos, dict):
        return {str(k): str(v) for k, v in brutos.items()}
    return mapa


def _transporte_urllib(url: str) -> RespostaHttp:
    """Fetch pontual **sem** seguir redirects (SSRF: cada hop é revalidado fora)."""
    pedido = Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
        method="GET",
    )
    opener = build_opener(_SemRedirect)
    try:
        with opener.open(pedido, timeout=TIMEOUT_S) as resposta:  # noqa: S310 — URL já validada
            estado = int(getattr(resposta, "status", 200) or 200)
            cabecalhos = _cabecalhos_mapa(getattr(resposta, "headers", None))
            corpo = resposta.read(LIMITE_BYTES + 1)
    except HTTPError as erro:
        # Com ``_SemRedirect``, 3xx chega aqui como HTTPError (não é seguido).
        estado = int(erro.code)
        cabecalhos = _cabecalhos_mapa(getattr(erro, "headers", None))
        try:
            corpo = erro.read(LIMITE_BYTES + 1)
        except Exception:  # noqa: BLE001 — corpo opcional em erros HTTP
            corpo = b""
    except URLError as erro:
        raise UrlRecusada(url) from erro

    if len(corpo) > LIMITE_BYTES:
        raise UrlRecusada(url, "Endereço privado recusado.")
    return RespostaHttp(estado=estado, corpo=corpo, cabecalhos=cabecalhos, url=url)


def _extrair_html(corpo: bytes, tipo_conteudo: str) -> str:
    charset = "utf-8"
    if "charset=" in tipo_conteudo.lower():
        charset = tipo_conteudo.lower().split("charset=", 1)[1].split(";")[0].strip() or charset
    try:
        html = corpo.decode(charset, errors="replace")
    except LookupError:
        html = corpo.decode("utf-8", errors="replace")

    if "html" not in tipo_conteudo.lower() and not re.search(r"<html|<body|<p|<article", html, re.I):
        return html.strip()

    extrator = _ExtratorTexto()
    extrator.feed(html)
    extrator.close()
    texto = extrator.texto()
    titulo = extrator.titulo.strip()
    if titulo and titulo not in texto:
        return f"{titulo}\n\n{texto}".strip()
    return texto.strip()


def obter_texto_url(
    url: str,
    *,
    resolver: ResolverDns | None = None,
    transporte: Transporte | None = None,
) -> str:
    """Descarrega a URL (com revalidação em cada redirect) e devolve texto principal."""
    actual = url
    transporte_efectivo = transporte or _transporte_urllib

    for _ in range(MAX_REDIRECTS + 1):
        validar_url(actual, resolver=resolver)
        resposta = transporte_efectivo(actual)
        if 300 <= resposta.estado < 400:
            localizacao = resposta.cabecalhos.get("Location") or resposta.cabecalhos.get(
                "location"
            )
            if not localizacao:
                raise UrlRecusada(actual)
            seguinte = urljoin(actual, localizacao)
            # Revalidar destino antes de qualquer fetch ao alvo do redirect.
            validar_url(seguinte, resolver=resolver)
            actual = seguinte
            continue
        if resposta.estado >= 400:
            raise UrlRecusada(actual)
        tipo = resposta.cabecalhos.get("Content-Type") or resposta.cabecalhos.get(
            "content-type"
        ) or "text/html"
        texto = _extrair_html(resposta.corpo, tipo)
        if not texto:
            raise UrlRecusada(actual)
        return texto

    raise UrlRecusada(url)


def ingestir_url(
    ligacao: sqlite3.Connection,
    url: str,
    destino: Path | str,
    *,
    resolver: ResolverDns | None = None,
    transporte: Transporte | None = None,
) -> DocumentoRegisto:
    """Obtém o texto do artigo e regista-o na biblioteca como documento."""
    texto = obter_texto_url(url, resolver=resolver, transporte=transporte)
    return registar_texto(ligacao, texto, destino)


def codigo_erro_url(exc: BaseException) -> str | None:
    """Código estável para a API: ``url_privada`` quando a URL foi recusada."""
    if isinstance(exc, UrlRecusada):
        return exc.codigo
    return None
