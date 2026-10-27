"""HTTP-alerts-list / create / toggle — liga ``engine.alertas`` à Starlette."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from engine.alertas.criar import criar_alerta, definir_activo, listar_alertas
from engine.alertas.limite import LimiteAlertas
from engine.api.erros import PEDIDO_INVALIDO, resposta_erro
from engine.api.ids import chat_id, formatar
from engine.armazenamento.repositorio import abrir


def _ligacao(request: Request) -> sqlite3.Connection:
    return abrir(Path(request.app.state.caminho_sqlite))


def _ale_id(numero: int) -> str:
    return formatar("ale", numero)


def _analisar_ale(valor: str) -> int:
    prefixo = "ale_"
    if not valor.startswith(prefixo) or not valor[len(prefixo) :].isdigit():
        raise ValueError("alerta_id inválido")
    return int(valor[len(prefixo) :])


def _dto(alerta: object) -> dict:
    return {
        "id": _ale_id(int(alerta.id)),  # type: ignore[attr-defined]
        "texto": alerta.consulta,  # type: ignore[attr-defined]
        "activo": bool(alerta.activo),  # type: ignore[attr-defined]
        "chat_id": chat_id(int(alerta.conversa_id)),  # type: ignore[attr-defined]
    }


async def listar(request: Request) -> Response:
    if getattr(request.app.state, "caminho_sqlite", None) is None:
        return JSONResponse({"itens": []})
    itens = [_dto(a) for a in listar_alertas(_ligacao(request))]
    return JSONResponse({"itens": itens})


async def criar(request: Request) -> Response:
    try:
        corpo = await request.json()
    except Exception:
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
    if not isinstance(corpo, dict):
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
    texto = str(corpo.get("texto") or "").strip()
    lente = corpo.get("lente") or "investigar"
    if not texto:
        return resposta_erro(400, PEDIDO_INVALIDO, "Texto do alerta em falta.")
    if getattr(request.app.state, "caminho_sqlite", None) is None:
        return resposta_erro(400, PEDIDO_INVALIDO, "SQLite não configurado.")
    ligacao = _ligacao(request)
    try:
        alerta = criar_alerta(ligacao, texto, lente=str(lente))
        ligacao.commit()
    except LimiteAlertas:
        return JSONResponse(
            {"erro": "limite_alertas", "mensagem": "Máximo de dez alertas."},
            status_code=409,
        )
    except ValueError as exc:
        return resposta_erro(400, PEDIDO_INVALIDO, str(exc))
    dto = _dto(alerta)
    return JSONResponse(
        {"id": dto["id"], "chat_id": dto["chat_id"], "activo": True},
        status_code=201,
    )


async def interruptor(request: Request) -> Response:
    bruto = str(request.path_params.get("alerta_id") or "")
    try:
        numero = _analisar_ale(bruto)
    except ValueError:
        return resposta_erro(400, PEDIDO_INVALIDO, "alerta_id inválido.")
    try:
        corpo = await request.json()
    except Exception:
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
    if not isinstance(corpo, dict) or "activo" not in corpo:
        return resposta_erro(400, PEDIDO_INVALIDO, "activo obrigatório.")
    activo = bool(corpo["activo"])
    ligacao = _ligacao(request)
    try:
        alerta = definir_activo(ligacao, numero, activo)
        ligacao.commit()
    except KeyError:
        return resposta_erro(404, PEDIDO_INVALIDO, "Alerta inexistente.")
    return JSONResponse({"id": _ale_id(alerta.id), "activo": bool(alerta.activo)})


def rotas_alertas() -> list[Route]:
    return [
        Route("/alerts", listar, methods=["GET"]),
        Route("/alerts", criar, methods=["POST"]),
        Route("/alerts/{alerta_id}", interruptor, methods=["PATCH"]),
    ]
