"""Caminho feliz: ingestão .md → FTS → POST /search com excerto."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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
    app = criar_app(caminho_sqlite=caminho_tmp, pasta_uploads=uploads)
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
