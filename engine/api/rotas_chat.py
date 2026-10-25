"""Rotas de chat e procura (HTTP-chat-*, HTTP-search)."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.routing import Route

from engine.api import conversas as repo
from engine.api.erros import (
    CHAT_INEXISTENTE,
    FILA_OCUPADA,
    PEDIDO_INVALIDO,
    resposta_erro,
)
from engine.api.ids import IdInvalido, analisar_chat
from engine.armazenamento.repositorio import abrir
from engine.escalonador.estados import FilaOcupada

MotorProcura = Callable[..., dict[str, Any]]


def _ligacao(request: Request) -> sqlite3.Connection:
    caminho: Path = request.app.state.caminho_sqlite
    return abrir(caminho)


def _motor(request: Request) -> MotorProcura:
    return request.app.state.motor_procura


def _slot(request: Request):
    return request.app.state.slot


async def listar_chats(request: Request) -> Response:
    ligacao = _ligacao(request)
    return _json({"itens": repo.listar_conversas(ligacao)})


async def criar_chat(request: Request) -> Response:
    corpo: dict[str, Any] = {}
    if request.headers.get("content-length") not in (None, "0"):
        try:
            corpo = await request.json()
        except Exception:
            corpo = {}
    titulo = corpo.get("titulo") if isinstance(corpo, dict) else None
    if titulo is not None and not isinstance(titulo, str):
        return resposta_erro(400, PEDIDO_INVALIDO, "titulo inválido")
    criada = repo.criar_conversa(_ligacao(request), titulo=titulo)
    return _json(criada, status=201)


async def obter_chat(request: Request) -> Response:
    try:
        numero = analisar_chat(request.path_params["chat_id"])
    except IdInvalido:
        return resposta_erro(404, CHAT_INEXISTENTE, "Conversa inexistente.")
    detalhe = repo.obter_conversa(_ligacao(request), numero)
    if detalhe is None:
        return resposta_erro(404, CHAT_INEXISTENTE, "Conversa inexistente.")
    return _json(detalhe)


async def renomear_chat(request: Request) -> Response:
    try:
        numero = analisar_chat(request.path_params["chat_id"])
    except IdInvalido:
        return resposta_erro(404, CHAT_INEXISTENTE, "Conversa inexistente.")
    try:
        corpo = await request.json()
    except Exception:
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
    titulo = corpo.get("titulo") if isinstance(corpo, dict) else None
    if not isinstance(titulo, str) or not titulo.strip():
        return resposta_erro(400, PEDIDO_INVALIDO, "titulo obrigatório.")
    actualizado = repo.renomear_conversa(_ligacao(request), numero, titulo.strip())
    if actualizado is None:
        return resposta_erro(404, CHAT_INEXISTENTE, "Conversa inexistente.")
    return _json(actualizado)


async def apagar_chat(request: Request) -> Response:
    try:
        numero = analisar_chat(request.path_params["chat_id"])
    except IdInvalido:
        return resposta_erro(404, CHAT_INEXISTENTE, "Conversa inexistente.")
    if not repo.apagar_conversa(_ligacao(request), numero):
        return resposta_erro(404, CHAT_INEXISTENTE, "Conversa inexistente.")
    return Response(status_code=204)


async def procurar(request: Request) -> Response:
    try:
        corpo = await request.json()
    except Exception:
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
    if not isinstance(corpo, dict):
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")

    chat_bruto = corpo.get("chat_id")
    texto = corpo.get("texto")
    lente = corpo.get("lente")
    if not isinstance(chat_bruto, str) or not isinstance(texto, str) or not texto.strip():
        return resposta_erro(400, PEDIDO_INVALIDO, "chat_id e texto são obrigatórios.")
    if lente is not None and lente not in {
        "investigar",
        "assessment",
        "acreditacao",
        "verificar",
    }:
        return resposta_erro(400, PEDIDO_INVALIDO, "lente inválida.")

    try:
        numero = analisar_chat(chat_bruto)
    except IdInvalido:
        return resposta_erro(404, CHAT_INEXISTENTE, "Conversa inexistente.")

    ligacao = _ligacao(request)
    if repo.obter_conversa(ligacao, numero) is None:
        return resposta_erro(404, CHAT_INEXISTENTE, "Conversa inexistente.")

    slot = _slot(request)
    try:
        with slot.adquirir("search"):
            resultado = _motor(request)(
                chat_id=chat_bruto,
                texto=texto.strip(),
                lente=lente or "investigar",
                pagina_aberta=corpo.get("pagina_aberta"),
                com_e2b=bool(request.app.state.com_e2b),
            )
    except FilaOcupada as exc:
        return resposta_erro(409, FILA_OCUPADA, str(exc.mensagem))

    if not isinstance(resultado, dict):
        resultado = {"excertos": [], "frases": [], "miniaturas": []}

    # Sem E2B: nunca emitir prosa mesmo que o motor a invente
    if not request.app.state.com_e2b:
        resultado = {
            **resultado,
            "frases": [],
        }

    repo.nomear_pela_primeira_procura(ligacao, numero, texto.strip())
    mensagem_id = repo.gravar_turno_procura(
        ligacao,
        conversa_numero=numero,
        texto_utilizador=texto.strip(),
        lente=lente,
        resultado=resultado,
    )

    return StreamingResponse(
        _gerar_sse(resultado, mensagem_id=mensagem_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _gerar_sse(resultado: dict[str, Any], *, mensagem_id: str) -> Iterator[bytes]:
    miniaturas = list(resultado.get("miniaturas") or [])
    if miniaturas:
        yield _sse({"tipo": "miniaturas", "itens": miniaturas})

    excertos = list(resultado.get("excertos") or [])
    for ex in excertos:
        evento = {"tipo": "excerto", **ex}
        yield _sse(evento)

    # Frases só depois das portas — lista já filtrada pelo motor
    frases = list(resultado.get("frases") or [])
    for frase in frases:
        if isinstance(frase, str):
            yield _sse({"tipo": "frase", "texto": frase, "citacoes": []})
        elif isinstance(frase, dict):
            yield _sse({"tipo": "frase", **frase})

    if not excertos and not frases:
        yield _sse({"tipo": "vazio", "motivo": "nenhuma_frase_acima_do_limiar"})

    yield _sse({"tipo": "fim", "mensagem_id": mensagem_id})


def _sse(payload: dict[str, Any]) -> bytes:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")


def _json(corpo: dict[str, Any], *, status: int = 200) -> Response:
    return Response(
        json.dumps(corpo, ensure_ascii=False).encode("utf-8"),
        status_code=status,
        media_type="application/json",
    )


def rotas_chat() -> list[Route]:
    return [
        Route("/chats", listar_chats, methods=["GET"]),
        Route("/chats", criar_chat, methods=["POST"]),
        Route("/chats/{chat_id}", obter_chat, methods=["GET"]),
        Route("/chats/{chat_id}", renomear_chat, methods=["PATCH"]),
        Route("/chats/{chat_id}", apagar_chat, methods=["DELETE"]),
        Route("/search", procurar, methods=["POST"]),
    ]
