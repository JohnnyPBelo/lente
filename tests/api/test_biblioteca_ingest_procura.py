"""Caminho feliz: ingestão .md/URL → FTS → POST /search com excerto e miniatura."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from starlette.testclient import TestClient

from engine.api.app import criar_app

FIXTORES = Path(__file__).resolve().parents[1] / "fixtures" / "ingestao"


def _eventos_sse(corpo: str) -> list[dict[str, Any]]:
    eventos: list[dict[str, Any]] = []
    for bloco in corpo.split("\n\n"):
        bloco = bloco.strip()
        if not bloco:
            continue
        for linha in bloco.splitlines():
            if linha.startswith("data:"):
                eventos.append(json.loads(linha[5:].strip()))
    return eventos


def test_ingest_md_e_procura_devolve_excerto(caminho_tmp: Path, tmp_path: Path) -> None:
    uploads = tmp_path / "biblioteca"
    thumbs = tmp_path / "miniaturas"
    app = criar_app(
        caminho_sqlite=caminho_tmp,
        pasta_uploads=uploads,
        pasta_miniaturas=thumbs,
    )
    cliente = TestClient(app)

    amostra = FIXTORES / "amostra.md"
    with amostra.open("rb") as fh:
        resp = cliente.post(
            "/library/ingest",
            files={"ficheiros": ("amostra.md", fh, "text/markdown")},
        )
    assert resp.status_code == 202
    corpo = resp.json()
    assert corpo["estado"] == "ok"
    assert str(corpo["documento_id"]).startswith("doc_")

    lista = cliente.get("/library").json()
    assert any(i["id"] == corpo["documento_id"] for i in lista["itens"])

    chat = cliente.post("/chats", json={}).json()
    procura = cliente.post(
        "/search",
        json={
            "chat_id": chat["id"],
            "texto": "amostra Markdown",
            "lente": "investigar",
        },
    )
    assert procura.status_code == 200
    eventos = _eventos_sse(procura.text)
    excertos = [e for e in eventos if e.get("tipo") == "excerto"]
    assert excertos, f"esperava excertos, eventos={eventos}"
    assert "amostra" in excertos[0]["texto"].lower()
    assert excertos[0]["documento_id"] == corpo["documento_id"]

    miniaturas = [e for e in eventos if e.get("tipo") == "miniaturas"]
    assert miniaturas, f"esperava miniaturas, eventos={eventos}"
    item = miniaturas[0]["itens"][0]
    assert item["documento_id"] == corpo["documento_id"]
    assert item["url"].startswith("/media/thumbs/")
    assert item["url"].endswith(".png")
    thumb = cliente.get(item["url"])
    assert thumb.status_code == 200
    assert thumb.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_ingest_url_indexa_e_procura(
    caminho_tmp: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """URL pública (transporte mock) entra no índice FTS e aparece na procura."""
    texto_artigo = (
        "Parágrafo principal do artigo público sintético sobre política de acesso."
    )

    def obter_mock(url: str, **_kwargs: Any) -> str:
        assert "exemplo.test" in url
        return texto_artigo

    monkeypatch.setattr("engine.ingestao.url.obter_texto_url", obter_mock)

    uploads = tmp_path / "biblioteca"
    thumbs = tmp_path / "miniaturas"
    app = criar_app(
        caminho_sqlite=caminho_tmp,
        pasta_uploads=uploads,
        pasta_miniaturas=thumbs,
    )
    cliente = TestClient(app)

    resp = cliente.post(
        "/library/ingest",
        json={"url": "http://exemplo.test/artigo-politica"},
    )
    assert resp.status_code == 202
    corpo = resp.json()
    assert corpo["estado"] == "ok"
    assert str(corpo["documento_id"]).startswith("doc_")
    assert corpo["documento_id"] != "doc_0"

    lista = cliente.get("/library").json()
    assert any(i["id"] == corpo["documento_id"] for i in lista["itens"])

    chat = cliente.post("/chats", json={}).json()
    procura = cliente.post(
        "/search",
        json={
            "chat_id": chat["id"],
            "texto": "política de acesso",
            "lente": "investigar",
        },
    )
    assert procura.status_code == 200
    eventos = _eventos_sse(procura.text)
    excertos = [e for e in eventos if e.get("tipo") == "excerto"]
    assert excertos, f"esperava excertos após URL, eventos={eventos}"
    assert "acesso" in excertos[0]["texto"].lower()
    assert excertos[0]["documento_id"] == corpo["documento_id"]

    miniaturas = [e for e in eventos if e.get("tipo") == "miniaturas"]
    assert miniaturas
    assert miniaturas[0]["itens"][0]["url"].startswith("/media/thumbs/")


def test_ingest_url_privada_recusada(caminho_tmp: Path, tmp_path: Path) -> None:
    app = criar_app(
        caminho_sqlite=caminho_tmp,
        pasta_uploads=tmp_path / "biblioteca",
        pasta_miniaturas=tmp_path / "miniaturas",
    )
    cliente = TestClient(app)
    resp = cliente.post("/library/ingest", json={"url": "http://127.0.0.1/interno"})
    assert resp.status_code == 400
    corpo = resp.json()
    assert corpo["erro"] == "url_privada"
    assert "privado" in corpo["mensagem"].lower()
