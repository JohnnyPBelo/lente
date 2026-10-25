"""Regressão REG-HTTP-001: POST /search em SSE com prova ou vazio."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from starlette.testclient import TestClient

from engine.api.app import criar_app
from engine.armazenamento.repositorio import abrir


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


def _inserir_documento_minimo(caminho: Path) -> str:
    """Fixture indexada mínima: um documento e uma frase com offsets."""
    ligacao = abrir(caminho)
    agora = "2026-10-25T00:00:00Z"
    cur = ligacao.execute(
        "INSERT INTO documentos "
        "(caminho, titulo, tipo, sha256, estado, paginas, criado_em, actualizado_em) "
        "VALUES (?, ?, 'txt', ?, 'ok', 1, ?, ?)",
        ("/tmp/politica-acesso.txt", "Politica de acesso remoto", "a" * 64, agora, agora),
    )
    doc_id = int(cur.lastrowid)
    cur = ligacao.execute(
        "INSERT INTO documento_hashes (documento_id, sha256, visto_em, activa) "
        "VALUES (?, ?, ?, 1)",
        (doc_id, "a" * 64, agora),
    )
    hash_id = int(cur.lastrowid)
    cur = ligacao.execute(
        "INSERT INTO blocos "
        "(documento_id, hash_id, ordem, texto, offset_inicio, offset_fim, tokens_aprox) "
        "VALUES (?, ?, 0, ?, 0, 80, 12)",
        (
            doc_id,
            hash_id,
            "O acesso remoto exige aprovação do responsável de segurança.",
        ),
    )
    bloco_id = int(cur.lastrowid)
    ligacao.execute(
        "INSERT INTO frases "
        "(bloco_id, documento_id, pagina, texto, offset_inicio, offset_fim, ordem) "
        "VALUES (?, ?, 4, ?, 120, 188, 0)",
        (
            bloco_id,
            doc_id,
            "O acesso remoto exige aprovação do responsável de segurança.",
        ),
    )
    ligacao.commit()
    return f"doc_{doc_id}"


def test_reg_http_001(caminho_tmp: Path) -> None:
    """POST /search: SSE 200 com excerto (doc+offsets) ou vazio; sem prosa crua."""
    abrir(caminho_tmp)
    documento_id = _inserir_documento_minimo(caminho_tmp)

    def motor_com_excerto(*, chat_id: str, texto: str, lente: str, **_kwargs):
        del chat_id, texto, lente
        return {
            "miniaturas": [
                {
                    "documento_id": documento_id,
                    "pagina": 4,
                    "url": f"/media/thumbs/{documento_id}_p4.webp",
                }
            ],
            "excertos": [
                {
                    "n": 1,
                    "documento_id": documento_id,
                    "pagina": 4,
                    "texto": (
                        "O acesso remoto exige aprovação do responsável de segurança."
                    ),
                    "offsets": {"inicio": 120, "fim": 188},
                    "caixas": [],
                    "score_juiz": 0.82,
                }
            ],
            "frases": [],  # sem E2B: nunca prosa
        }

    app = criar_app(
        caminho_sqlite=caminho_tmp,
        motor_procura=motor_com_excerto,
        com_e2b=False,
    )
    cliente = TestClient(app)

    chat = cliente.post("/chats", json={}).json()
    chat_id = chat["id"]

    resposta = cliente.post(
        "/search",
        json={
            "chat_id": chat_id,
            "texto": "Quem aprova o acesso remoto?",
            "lente": "investigar",
        },
    )
    assert resposta.status_code == 200
    assert "text/event-stream" in resposta.headers["content-type"]

    eventos = _eventos_sse(resposta.text)
    tipos = [e["tipo"] for e in eventos]
    assert "fim" in tipos

    # Nunca prosa sem lista de frases já filtrada (sem E2B: zero frases)
    frases = [e for e in eventos if e.get("tipo") == "frase"]
    assert frases == []

    excertos = [e for e in eventos if e.get("tipo") == "excerto"]
    vazios = [e for e in eventos if e.get("tipo") == "vazio"]
    assert excertos or vazios

    if excertos:
        ex = excertos[0]
        assert ex["documento_id"] == documento_id
        assert "offsets" in ex
        assert ex["offsets"]["inicio"] == 120
        assert ex["offsets"]["fim"] == 188

    assert resposta.status_code == 200
