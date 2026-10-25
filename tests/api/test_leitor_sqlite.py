"""Leitor HTTP lê documentos indexados no SQLite (não inventa páginas vazias)."""

from __future__ import annotations

from pathlib import Path

from starlette.testclient import TestClient

from engine.api.app import criar_app

FIXTORES = Path(__file__).resolve().parents[1] / "fixtures" / "ingestao"


def test_documento_e_pagina_apos_ingest(caminho_tmp: Path, tmp_path: Path) -> None:
    app = criar_app(
        caminho_sqlite=caminho_tmp,
        pasta_uploads=tmp_path / "biblioteca",
        pasta_miniaturas=tmp_path / "miniaturas",
    )
    cliente = TestClient(app)

    amostra = FIXTORES / "amostra.md"
    with amostra.open("rb") as fh:
        resp = cliente.post(
            "/library/ingest",
            files={"ficheiros": ("amostra.md", fh, "text/markdown")},
        )
    assert resp.status_code == 202
    doc = resp.json()["documento_id"]

    meta = cliente.get(f"/documents/{doc}")
    assert meta.status_code == 200
    corpo = meta.json()
    assert corpo["id"] == doc
    assert corpo["titulo"]
    assert corpo["hash_sha256"]
    assert corpo["hash_sha256"] != "a" * 64

    pagina = cliente.get(f"/documents/{doc}/pages/1")
    assert pagina.status_code == 200
    texto = pagina.json()["texto"]
    assert "amostra" in texto.lower() or "markdown" in texto.lower()

    ausente = cliente.get("/documents/doc_99999")
    assert ausente.status_code == 404
    assert ausente.json()["erro"] == "documento_inexistente"
