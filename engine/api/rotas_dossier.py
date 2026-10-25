"""Rotas HTTP do dossier: fecho, reabrir e export (HTTP-dossier-*)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from engine.api.erros import (
    CHAT_INEXISTENTE,
    DOSSIER_INEXISTENTE,
    PEDIDO_INVALIDO,
    resposta_erro,
)
from engine.api.ids import IdInvalido, analisar_chat, analisar_dos, chat_id, dos_id
from engine.armazenamento.repositorio import abrir
from engine.dossier.exportar import exportar_dossier
from engine.dossier.fechar import fechar_dossier
from engine.dossier.reabrir import reabrir_dossier


def _ligacao(request: Request) -> sqlite3.Connection:
    caminho: Path = request.app.state.caminho_sqlite
    return abrir(caminho)


def _json(corpo: dict[str, Any], *, status: int = 200) -> Response:
    return Response(
        json.dumps(corpo, ensure_ascii=False).encode("utf-8"),
        status_code=status,
        media_type="application/json",
    )


async def fechar(request: Request) -> Response:
    """POST /chats/{chat_id}/dossier — fecho explícito (botão)."""
    try:
        conversa = analisar_chat(request.path_params["chat_id"])
    except IdInvalido:
        return resposta_erro(404, CHAT_INEXISTENTE, "Conversa inexistente.")

    ligacao = _ligacao(request)
    existe = ligacao.execute(
        "SELECT 1 FROM conversas WHERE id = ? AND apagada = 0", (conversa,)
    ).fetchone()
    if existe is None:
        return resposta_erro(404, CHAT_INEXISTENTE, "Conversa inexistente.")

    try:
        resultado = fechar_dossier(ligacao, conversa)
        ligacao.commit()
    except ValueError as exc:
        return resposta_erro(400, PEDIDO_INVALIDO, str(exc))
    return _json(resultado, status=201)


async def obter(request: Request) -> Response:
    """GET /dossiers/{dossier_id} — reabrir fotografia; ``fonte_alterada``."""
    try:
        numero = analisar_dos(request.path_params["dossier_id"])
    except IdInvalido:
        return resposta_erro(404, DOSSIER_INEXISTENTE, "Dossier inexistente.")

    ligacao = _ligacao(request)
    try:
        vista = reabrir_dossier(ligacao, numero)
    except ValueError:
        return resposta_erro(404, DOSSIER_INEXISTENTE, "Dossier inexistente.")

    conversa = vista.get("conversa_id")
    return _json(
        {
            "id": vista.get("id") or dos_id(numero),
            "chat_id": chat_id(int(conversa)) if conversa is not None else None,
            "fonte_alterada": bool(vista.get("fonte_alterada")),
            "frases": vista.get("frases") or [],
            "perguntas": vista.get("perguntas") or [],
            "ficheiros": vista.get("ficheiros") or [],
            "versoes_modelo": vista.get("versoes_modelo"),
            "fechado_em": vista.get("fechado_em"),
            "titulo": vista.get("titulo"),
        }
    )


async def exportar(request: Request) -> Response:
    """GET /dossiers/{dossier_id}/export — URLs Markdown + JSON."""
    bruto = request.path_params["dossier_id"]
    try:
        numero = analisar_dos(bruto)
    except IdInvalido:
        return resposta_erro(404, DOSSIER_INEXISTENTE, "Dossier inexistente.")

    ligacao = _ligacao(request)
    existe = ligacao.execute(
        "SELECT 1 FROM dossiers WHERE id = ?", (numero,)
    ).fetchone()
    if existe is None:
        return resposta_erro(404, DOSSIER_INEXISTENTE, "Dossier inexistente.")

    publico = dos_id(numero)
    return _json(
        {
            "markdown_url": f"/dossiers/{publico}/export.md",
            "json_url": f"/dossiers/{publico}/export.json",
        }
    )


async def exportar_markdown(request: Request) -> Response:
    try:
        numero = analisar_dos(request.path_params["dossier_id"])
    except IdInvalido:
        return resposta_erro(404, DOSSIER_INEXISTENTE, "Dossier inexistente.")
    ligacao = _ligacao(request)
    try:
        markdown, _arquivo = exportar_dossier(ligacao, numero)
    except ValueError:
        return resposta_erro(404, DOSSIER_INEXISTENTE, "Dossier inexistente.")
    return Response(
        markdown.encode("utf-8"),
        status_code=200,
        media_type="text/markdown; charset=utf-8",
    )


async def exportar_json(request: Request) -> Response:
    try:
        numero = analisar_dos(request.path_params["dossier_id"])
    except IdInvalido:
        return resposta_erro(404, DOSSIER_INEXISTENTE, "Dossier inexistente.")
    ligacao = _ligacao(request)
    try:
        _markdown, arquivo = exportar_dossier(ligacao, numero)
    except ValueError:
        return resposta_erro(404, DOSSIER_INEXISTENTE, "Dossier inexistente.")
    return _json(arquivo)


def rotas_dossier() -> list[Route]:
    return [
        Route("/chats/{chat_id}/dossier", fechar, methods=["POST"]),
        Route("/dossiers/{dossier_id}", obter, methods=["GET"]),
        Route("/dossiers/{dossier_id}/export", exportar, methods=["GET"]),
        Route("/dossiers/{dossier_id}/export.md", exportar_markdown, methods=["GET"]),
        Route("/dossiers/{dossier_id}/export.json", exportar_json, methods=["GET"]),
    ]
