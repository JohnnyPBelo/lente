"""HTTP-backup — zip local de ``data/``, sem nuvem."""

from __future__ import annotations

from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from engine.api.erros import PEDIDO_INVALIDO, resposta_erro
from engine.backup.zip_data import PastaDataInexistente, criar_copia


def _pasta_data(request: Request) -> Path:
    configurada = getattr(request.app.state, "pasta_data", None)
    if configurada is not None:
        return Path(configurada)
    sqlite = getattr(request.app.state, "caminho_sqlite", None)
    if sqlite is not None:
        return Path(sqlite).parent
    return Path("data")


async def backup(request: Request) -> Response:
    try:
        corpo = await request.json()
    except Exception:
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
    if not isinstance(corpo, dict):
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
    destino = corpo.get("destino")
    if not isinstance(destino, str) or not destino.strip():
        return resposta_erro(400, PEDIDO_INVALIDO, "destino obrigatório.")
    try:
        caminho = criar_copia(_pasta_data(request), destino.strip())
    except PastaDataInexistente as exc:
        return resposta_erro(400, PEDIDO_INVALIDO, str(exc))
    except OSError as exc:
        return resposta_erro(400, PEDIDO_INVALIDO, str(exc) or "falha no backup")
    bytes_zip = caminho.stat().st_size if caminho.is_file() else 0
    return JSONResponse({"bytes": bytes_zip, "caminho": str(caminho)})


def rotas_backup() -> list[Route]:
    return [Route("/backup", backup, methods=["POST"])]
