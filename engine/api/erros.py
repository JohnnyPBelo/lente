"""Códigos de erro HTTP estáveis para a UI."""

from __future__ import annotations

from typing import Any

from starlette.responses import JSONResponse

# Códigos estáveis referidos no plano e no contrato
URL_RECUSADA = "url_recusada"
URL_PRIVADA = "url_privada"
FILA_OCUPADA = "fila_ocupada"
LIMIAR_VAZIO = "limiar_vazio"
CHAT_INEXISTENTE = "chat_inexistente"
PEDIDO_INVALIDO = "pedido_invalido"
BIND_PUBLICO = "bind_publico"


def corpo_erro(erro: str, mensagem: str) -> dict[str, str]:
    return {"erro": erro, "mensagem": mensagem}


def resposta_erro(
    status: int,
    erro: str,
    mensagem: str,
    *,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        corpo_erro(erro, mensagem),
        status_code=status,
        headers=headers,
    )


def mensagem_de_excepcao(exc: BaseException) -> str:
    texto = getattr(exc, "mensagem", None)
    if isinstance(texto, str) and texto:
        return texto
    return str(exc) or exc.__class__.__name__


def as_dict(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    return {}
