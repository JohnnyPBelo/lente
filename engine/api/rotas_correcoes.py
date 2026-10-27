"""HTTP-corrections-export / import — sem pesos LoRA."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from engine.api.erros import PEDIDO_INVALIDO, resposta_erro
from engine.armazenamento.repositorio import abrir
from engine.feedback.exportar_correcoes import exportar_correcoes
from engine.feedback.importar_correcoes import (
    ModeloBaseIncompativel,
    importar_correcoes,
    previsualizar_importacao,
)
from engine.feedback.schema_correcoes import CorrecoesInvalidas


def _ligacao(request: Request) -> sqlite3.Connection:
    return abrir(Path(request.app.state.caminho_sqlite))


async def exportar(request: Request) -> Response:
    if getattr(request.app.state, "caminho_sqlite", None) is None:
        return resposta_erro(400, PEDIDO_INVALIDO, "SQLite não configurado.")
    return JSONResponse(exportar_correcoes(_ligacao(request)))


async def preview(request: Request) -> Response:
    try:
        corpo = await request.json()
    except Exception:
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
    if getattr(request.app.state, "caminho_sqlite", None) is None:
        return resposta_erro(400, PEDIDO_INVALIDO, "SQLite não configurado.")
    try:
        return JSONResponse(previsualizar_importacao(_ligacao(request), corpo))
    except CorrecoesInvalidas as exc:
        return resposta_erro(400, PEDIDO_INVALIDO, str(exc))


async def confirmar(request: Request) -> Response:
    try:
        corpo = await request.json()
    except Exception:
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
    if getattr(request.app.state, "caminho_sqlite", None) is None:
        return resposta_erro(400, PEDIDO_INVALIDO, "SQLite não configurado.")
    try:
        resultado = importar_correcoes(_ligacao(request), corpo, confirmar=True)
    except ModeloBaseIncompativel as exc:
        return resposta_erro(409, PEDIDO_INVALIDO, str(exc))
    except CorrecoesInvalidas as exc:
        return resposta_erro(400, PEDIDO_INVALIDO, str(exc))
    return JSONResponse(
        {
            "aceite": bool(resultado.get("aceite")),
            "treino_agendado": bool(resultado.get("treino_agendado")),
        },
        status_code=202,
    )


def rotas_correcoes() -> list[Route]:
    return [
        Route("/corrections/export", exportar, methods=["GET"]),
        Route("/corrections/import/preview", preview, methods=["POST"]),
        Route("/corrections/import/confirm", confirmar, methods=["POST"]),
    ]
