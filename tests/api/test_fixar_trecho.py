"""REG-LEI-008: fixar trecho persiste e reabre."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from starlette.testclient import TestClient

from engine.api.app import criar_app
from engine.api.rotas_documento import reiniciar_documento_falso
from engine.armazenamento.repositorio import abrir


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def test_reg_lei_008(caminho_tmp: Path) -> None:
    reiniciar_documento_falso()
    ligacao = abrir(caminho_tmp)
    momento = _agora()
    ligacao.execute(
        "INSERT INTO documentos "
        "(id, caminho, titulo, tipo, sha256, estado, paginas, criado_em, actualizado_em) "
        "VALUES (12, ?, 'Politica', 'texto', ?, 'ok', 1, ?, ?)",
        ("/tmp/politica.txt", "a" * 64, momento, momento),
    )
    ligacao.commit()

    app = criar_app(caminho_sqlite=caminho_tmp)
    cliente = TestClient(app)

    r = cliente.post(
        "/chats/cht_01/fixados",
        json={
            "documento_id": "doc_12",
            "pagina": 4,
            "texto": "O acesso remoto exige aprovação prévia.",
            "offsets": {"inicio": 0, "fim": 40},
        },
    )
    assert r.status_code == 201
    fix_id = r.json()["id"]
    assert fix_id

    lista = cliente.get("/chats/cht_01/fixados")
    assert lista.status_code == 200
    itens = lista.json()["itens"]
    assert len(itens) == 1
    assert itens[0]["id"] == fix_id
    assert itens[0]["texto"].startswith("O acesso remoto")

    # Documento inexistente → 404 (não inventa /tmp)
    falha = cliente.post(
        "/chats/cht_01/fixados",
        json={
            "documento_id": "doc_999",
            "pagina": 1,
            "texto": "fantasma",
            "offsets": {"inicio": 0, "fim": 8},
        },
    )
    assert falha.status_code == 404
    assert falha.json()["erro"] == "documento_inexistente"
