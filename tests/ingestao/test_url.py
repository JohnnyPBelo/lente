"""Regressão REG-ING-007: ingestão por URL pública e código estável url_privada."""

from __future__ import annotations

import ipaddress
import sqlite3
from pathlib import Path

import pytest

from engine.armazenamento.ligacao import abrir_ligacao
from engine.armazenamento.migracoes import aplicar_migracoes
from engine.ingestao.ssrf import UrlRecusada
from engine.ingestao.url import RespostaHttp, codigo_erro_url, ingestir_url, obter_texto_url


HTML_ARTIGO = (
    "<!DOCTYPE html><html><head><title>Artigo de teste</title></head>"
    "<body><article><p>Parágrafo principal do artigo público sintético.</p>"
    "</article></body></html>"
)


def _resolver_publico(host: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    assert host == "exemplo.test"
    return [ipaddress.ip_address("8.8.8.8")]


@pytest.fixture
def caminho_tmp(tmp_path: Path) -> Path:
    pasta = tmp_path / "data"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / "lente.sqlite"


@pytest.fixture
def ligacao(caminho_tmp: Path) -> sqlite3.Connection:
    aplicar_migracoes(caminho_tmp)
    lig = abrir_ligacao(caminho_tmp)
    yield lig
    lig.close()


def test_reg_ing_007(ligacao: sqlite3.Connection, tmp_path: Path) -> None:
    """URL pública mockada entra como documento; recusada → código url_privada."""

    def transporte_publico(url: str) -> RespostaHttp:
        assert "exemplo.test" in url
        return RespostaHttp(
            estado=200,
            corpo=HTML_ARTIGO.encode("utf-8"),
            cabecalhos={"Content-Type": "text/html; charset=utf-8"},
            url=url,
        )

    destino = tmp_path / "artigos" / "exemplo.txt"
    registo = ingestir_url(
        ligacao,
        "http://exemplo.test/artigo",
        destino,
        resolver=_resolver_publico,
        transporte=transporte_publico,
    )
    assert destino.is_file()
    assert "Parágrafo principal do artigo público sintético." in destino.read_text(
        encoding="utf-8"
    )

    linha = ligacao.execute(
        "SELECT id, estado FROM documentos WHERE id = ?",
        (registo.id,),
    ).fetchone()
    assert linha is not None
    assert linha["estado"] == "a_indexar"

    fila = ligacao.execute(
        "SELECT documento_id, estado FROM fila WHERE documento_id = ?",
        (registo.id,),
    ).fetchone()
    assert fila is not None
    assert fila["estado"] == "pendente"

    with pytest.raises(UrlRecusada) as contexto:
        obter_texto_url("http://127.0.0.1/interno")
    assert contexto.value.codigo == "url_privada"
    assert codigo_erro_url(contexto.value) == "url_privada"
    assert contexto.value.mensagem == "Endereço privado recusado."
