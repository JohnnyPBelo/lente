"""Rotas novas do fecho: upload limit, alerts, backup, tags, health honesty."""

from __future__ import annotations

from pathlib import Path

from starlette.testclient import TestClient

from engine.api.app import criar_app


def test_upload_excede_limite_devolve_413(caminho_tmp: Path, tmp_path: Path) -> None:
    app = criar_app(
        caminho_sqlite=caminho_tmp,
        pasta_uploads=tmp_path / "up",
        pasta_miniaturas=tmp_path / "th",
    )
    cliente = TestClient(app)
    # Pedaco acima do teto sem alocar 50 MiB reais: monkey via constante pequena.
    import engine.api.rotas_biblioteca as rb

    original = rb.LIMITE_UPLOAD_BYTES
    rb.LIMITE_UPLOAD_BYTES = 64
    try:
        resp = cliente.post(
            "/library/ingest",
            files={"ficheiros": ("grande.txt", b"x" * 200, "text/plain")},
        )
    finally:
        rb.LIMITE_UPLOAD_BYTES = original
    assert resp.status_code == 413
    assert resp.json()["erro"] == "pedido_invalido"


def test_alerts_criar_listar_toggle(caminho_tmp: Path) -> None:
    app = criar_app(caminho_sqlite=caminho_tmp)
    cliente = TestClient(app)
    cri = cliente.post("/alerts", json={"texto": "Novas VPN", "lente": "investigar"})
    assert cri.status_code == 201
    corpo = cri.json()
    assert corpo["id"].startswith("ale_")
    assert corpo["chat_id"].startswith("cht_")

    lista = cliente.get("/alerts").json()
    assert len(lista["itens"]) == 1
    assert lista["itens"][0]["texto"] == "Novas VPN"

    tog = cliente.patch(f"/alerts/{corpo['id']}", json={"activo": False})
    assert tog.status_code == 200
    assert tog.json()["activo"] is False


def test_backup_e_tags(caminho_tmp: Path, tmp_path: Path) -> None:
    uploads = tmp_path / "up"
    thumbs = tmp_path / "th"
    app = criar_app(
        caminho_sqlite=caminho_tmp,
        pasta_uploads=uploads,
        pasta_miniaturas=thumbs,
    )
    cliente = TestClient(app)
    ing = cliente.post(
        "/library/ingest",
        files={"ficheiros": ("a.txt", b"politica de acesso remoto", "text/plain")},
    )
    assert ing.status_code == 202
    doc_id = ing.json()["documento_id"]

    tags = cliente.put(
        f"/documents/{doc_id}/tags",
        json={"etiquetas": ["acesso", "vpn"]},
    )
    assert tags.status_code == 200
    assert tags.json()["etiquetas"] == ["acesso", "vpn"]

    destino = tmp_path / "copia.zip"
    bak = cliente.post("/backup", json={"destino": str(destino)})
    assert bak.status_code == 200
    assert destino.is_file()
    assert bak.json()["bytes"] > 0


def test_health_documenta_fts_e_limiar(caminho_tmp: Path) -> None:
    app = criar_app(caminho_sqlite=caminho_tmp)
    cliente = TestClient(app)
    h = cliente.get("/health").json()
    assert h["ok"] is True
    assert h["procura"] in {"fts", "fts_degradado"}
    assert "limiar" in h
    assert isinstance(h["limiar"], (int, float))


def test_correlate_sem_docs_nao_inventa_ids(caminho_tmp: Path) -> None:
    app = criar_app(caminho_sqlite=caminho_tmp)
    cliente = TestClient(app)
    r = cliente.post(
        "/correlate",
        json={
            "chat_id": "cht_1",
            "conceito_a": "acessos",
            "conceito_b": "auditoria",
            "lente": "investigar",
        },
    )
    assert r.status_code == 200
    assert r.json()["eventos"] == []


def test_models_download_sem_hub_e_honesto(caminho_tmp: Path, tmp_path: Path) -> None:
    """Escritor sem token/licença → 409; nunca inventa «a_descarregar» sem bytes."""
    modelos = tmp_path / "models"
    modelos.mkdir()
    app = criar_app(caminho_sqlite=caminho_tmp, raiz_modelos=modelos)
    cliente = TestClient(app)
    r = cliente.post("/models/download", json={"modelo": "escritor"})
    assert r.status_code == 409
    corpo = r.json()
    assert corpo.get("estado") != "a_descarregar"
    assert corpo.get("erro") in {"erro_licenca", "em_falta"} or "itens" in corpo


def test_feedback_acertou_apos_procura(caminho_tmp: Path, tmp_path: Path) -> None:
    """POST /feedback aceita Acertou sem bloquear e grava pares."""
    from engine.armazenamento.repositorio import abrir
    from engine.feedback.registar import listar_pares

    uploads = tmp_path / "up"
    thumbs = tmp_path / "th"
    app = criar_app(
        caminho_sqlite=caminho_tmp,
        pasta_uploads=uploads,
        pasta_miniaturas=thumbs,
    )
    cliente = TestClient(app)
    ing = cliente.post(
        "/library/ingest",
        files={"ficheiros": ("a.txt", b"politica de acesso remoto VPN", "text/plain")},
    )
    assert ing.status_code == 202
    chat = cliente.post("/chats", json={}).json()
    procura = cliente.post(
        "/search",
        json={
            "chat_id": chat["id"],
            "texto": "acesso remoto VPN",
            "lente": "investigar",
        },
    )
    assert procura.status_code == 200
    msg_id = None
    for bloco in procura.text.split("\n\n"):
        for linha in bloco.splitlines():
            if linha.startswith("data:"):
                import json

                ev = json.loads(linha[5:].strip())
                if ev.get("tipo") == "fim":
                    msg_id = ev.get("mensagem_id")
    assert msg_id

    fb = cliente.post(
        "/feedback",
        json={"mensagem_id": msg_id, "accao": "acertou"},
    )
    assert fb.status_code == 202
    corpo = fb.json()
    assert corpo["aceite"] is True
    assert corpo["treino_agendado"] is False
    assert listar_pares(abrir(caminho_tmp))


def test_feedback_descartar_nao_cria_pares(caminho_tmp: Path) -> None:
    from datetime import datetime, timezone

    from engine.armazenamento.repositorio import abrir
    from engine.feedback.registar import listar_pares

    ligacao = abrir(caminho_tmp)
    momento = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ligacao.execute(
        "INSERT INTO conversas (id, titulo, criado_em, actualizado_em, apagada) "
        "VALUES (1, 't', ?, ?, 0)",
        (momento, momento),
    )
    ligacao.execute(
        "INSERT INTO mensagens "
        "(id, conversa_id, papel, modo, lente, conteudo, meta_json, criado_em) "
        "VALUES (7, 1, 'assistente', 'procurar', 'investigar', '', '{}', ?)",
        (momento,),
    )
    ligacao.commit()

    app = criar_app(caminho_sqlite=caminho_tmp)
    cliente = TestClient(app)
    fb = cliente.post(
        "/feedback",
        json={"mensagem_id": "msg_7", "accao": "descartar"},
    )
    assert fb.status_code == 202
    assert fb.json()["aceite"] is True
    assert listar_pares(abrir(caminho_tmp)) == []
