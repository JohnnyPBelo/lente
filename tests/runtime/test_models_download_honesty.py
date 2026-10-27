"""#54 — /models/download não mente «a_descarregar» sem bytes."""

from __future__ import annotations

from pathlib import Path

from starlette.testclient import TestClient

from engine.api.app import criar_app


def test_download_escritor_sem_env_devolve_409(caminho_tmp: Path, tmp_path: Path) -> None:
    modelos = tmp_path / "models"
    modelos.mkdir()
    app = criar_app(caminho_sqlite=caminho_tmp, raiz_modelos=modelos)
    cliente = TestClient(app)
    resp = cliente.post("/models/download", json={"modelo": "escritor"})
    assert resp.status_code == 409
    corpo = resp.json()
    assert corpo.get("erro") == "erro_licenca"
    assert corpo.get("estado") != "a_descarregar"


def test_download_ja_pronto_devolve_200(caminho_tmp: Path, tmp_path: Path) -> None:
    modelos = tmp_path / "models"
    emb = modelos / "embeddinggemma-2"
    emb.mkdir(parents=True)
    (emb / "config.json").write_text("{}", encoding="utf-8")
    (emb / "model.safetensors").write_bytes(b"x")
    app = criar_app(caminho_sqlite=caminho_tmp, raiz_modelos=modelos)
    cliente = TestClient(app)
    resp = cliente.post("/models/download", json={"modelo": "embedding"})
    assert resp.status_code == 200
    assert resp.json()["estado"] == "pronto"


def test_status_reflecte_disco(caminho_tmp: Path, tmp_path: Path) -> None:
    modelos = tmp_path / "models"
    modelos.mkdir()
    app = criar_app(caminho_sqlite=caminho_tmp, raiz_modelos=modelos)
    cliente = TestClient(app)
    status = cliente.get("/models/status").json()
    assert status["embedding"]["estado"] == "em_falta"
    assert status["juiz"]["estado"] == "em_falta"
    assert status["escritor"]["estado"] == "em_falta"
    guia = cliente.get("/models/guidance").json()
    assert len(guia["itens"]) == 3
