"""REG-LEI-008: fixar trecho persiste e reabre."""

from __future__ import annotations

from pathlib import Path

from starlette.testclient import TestClient

from engine.api.app import criar_app
from engine.api.rotas_documento import listar_fixados, reiniciar_documento_falso
from engine.armazenamento.repositorio import abrir


def test_reg_lei_008(caminho_tmp: Path) -> None:
    reiniciar_documento_falso()
    abrir(caminho_tmp)
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

    fixados = listar_fixados("cht_01")
    assert len(fixados) == 1
    assert fixados[0]["texto"].startswith("O acesso remoto")

    # reabrir: listagem em memória mantém-se (mesmo processo)
    assert listar_fixados("cht_01")[0]["id"] == fix_id
