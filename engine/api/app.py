"""Aplicação ASGI Starlette: health, chat, procura, biblioteca, estáticos."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from engine.api.estaticos import montar_estaticos
from engine.api.motor import motor_procura_sem_e2b
from engine.api.rotas_biblioteca import rotas_biblioteca
from engine.api.rotas_chat import rotas_chat
from engine.api.rotas_dossier import rotas_dossier
from engine.armazenamento.repositorio import abrir
from engine.escalonador.slot import SlotPesado

MotorProcura = Callable[..., dict[str, Any]]

VERSAO = "0.0.0"


async def health(request: Request) -> JSONResponse:
    del request
    return JSONResponse(
        {
            "ok": True,
            "versao": VERSAO,
            "modelos": {
                "embedding": "ausente",
                "juiz": "ausente",
                "escritor": "ausente",
            },
            "disco_data_mb": 0,
        }
    )


def criar_app(
    *,
    caminho_sqlite: Path | str | None = None,
    motor_procura: MotorProcura | None = None,
    com_e2b: bool = False,
    slot: SlotPesado | None = None,
    raiz_estaticos: Path | str | None = None,
) -> Starlette:
    """Cria a app HTTP. BD tmp e motor em double nos testes."""
    caminho = Path(caminho_sqlite) if caminho_sqlite is not None else None
    if caminho is not None:
        abrir(caminho)

    rotas: list[Route] = [
        Route("/health", health, methods=["GET"]),
        *rotas_chat(),
        *rotas_biblioteca(),
        *rotas_dossier(),
    ]

    app = Starlette(routes=rotas)
    app.state.caminho_sqlite = caminho
    app.state.motor_procura = motor_procura or motor_procura_sem_e2b
    app.state.com_e2b = com_e2b
    app.state.slot = slot or SlotPesado()

    for mount in montar_estaticos(
        Path(raiz_estaticos) if raiz_estaticos is not None else None
    ):
        app.routes.append(mount)

    return app
