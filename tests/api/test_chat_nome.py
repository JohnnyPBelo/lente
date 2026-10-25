"""Regressão REG-CHT-002: a primeira procura nomeia a conversa."""

from __future__ import annotations

from pathlib import Path

from starlette.testclient import TestClient

from engine.api.app import criar_app
from engine.armazenamento.repositorio import abrir


def _motor_excertos_vazio(*, chat_id: str, texto: str, lente: str, **_kwargs):
    """Double: nenhum highlight (stream com vazio)."""
    del chat_id, texto, lente
    return {"excertos": [], "frases": [], "miniaturas": []}


def test_reg_cht_002(caminho_tmp: Path) -> None:
    """Conversa sem nome: a primeira procura deriva o título do texto."""
    abrir(caminho_tmp)

    app = criar_app(
        caminho_sqlite=caminho_tmp,
        motor_procura=_motor_excertos_vazio,
        com_e2b=False,
    )
    cliente = TestClient(app)

    criada = cliente.post("/chats", json={})
    assert criada.status_code == 201
    corpo = criada.json()
    chat_id = corpo["id"]
    assert corpo["titulo"] is None

    texto = "Quem aprova o acesso remoto?"
    resposta = cliente.post(
        "/search",
        json={"chat_id": chat_id, "texto": texto, "lente": "investigar"},
    )
    assert resposta.status_code == 200

    detalhe = cliente.get(f"/chats/{chat_id}")
    assert detalhe.status_code == 200
    assert detalhe.json()["titulo"] == texto

    lista = cliente.get("/chats")
    assert lista.status_code == 200
    itens = lista.json()["itens"]
    nosso = next(i for i in itens if i["id"] == chat_id)
    assert nosso["titulo"] == texto
