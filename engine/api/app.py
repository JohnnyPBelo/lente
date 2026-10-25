"""Aplicação ASGI Starlette: health, chat, procura, biblioteca, estáticos."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from engine.api.estaticos import caminho_dist, montar_estaticos
from engine.api.motor import motor_procura_sem_e2b
from engine.api.rotas_biblioteca import rotas_biblioteca
from engine.api.rotas_chat import rotas_chat
from engine.api.rotas_documento import rotas_documento
from engine.api.rotas_dossier import rotas_dossier
from engine.api.rotas_modelos import rotas_modelos
from engine.api.rotas_modos import rotas_modos
from engine.armazenamento.repositorio import abrir
from engine.escalonador.slot import SlotPesado
from engine.runtime.pesos import estados_health

MotorProcura = Callable[..., dict[str, Any]]

VERSAO = "0.0.0"

_PLACEHOLDER_HTML = """<!doctype html>
<html lang="pt">
<head><meta charset="utf-8"><title>Lente</title></head>
<body><main><h1>Lente</h1><p>Motor a escutar. Constrói a UI com Node 22.</p></main></body>
</html>
"""


async def health(request: Request) -> JSONResponse:
    raiz_modelos = getattr(request.app.state, "raiz_modelos", None)
    forcar = getattr(request.app.state, "forcar_estado_modelos", None)
    modelos = estados_health(raiz_modelos, forcar=forcar)
    disco = 0
    caminho = getattr(request.app.state, "caminho_sqlite", None)
    if caminho is not None:
        ficheiro = Path(caminho)
        if ficheiro.is_file():
            disco = max(1, ficheiro.stat().st_size // (1024 * 1024)) if ficheiro.stat().st_size >= 1024 * 1024 else 0
    return JSONResponse(
        {
            "ok": True,
            "versao": VERSAO,
            "modelos": modelos,
            "disco_data_mb": disco,
        }
    )


async def raiz_placeholder(request: Request) -> HTMLResponse:
    """UI construída ou placeholder — GET / devolve 200 sem exigir dist."""
    del request
    return HTMLResponse(_PLACEHOLDER_HTML, status_code=200)


def criar_app(
    *,
    caminho_sqlite: Path | str | None = None,
    motor_procura: MotorProcura | None = None,
    com_e2b: bool = False,
    slot: SlotPesado | None = None,
    raiz_estaticos: Path | str | None = None,
    raiz_modelos: Path | str | None = None,
    forcar_estado_modelos: dict[str, str] | None = None,
    descarregar_modelo: Callable[[str], dict[str, Any]] | None = None,
) -> Starlette:
    """Cria a app HTTP. BD tmp e motor em double nos testes."""
    caminho = Path(caminho_sqlite) if caminho_sqlite is not None else None
    if caminho is not None:
        abrir(caminho)

    rotas: list[Route] = [
        Route("/health", health, methods=["GET"]),
        *rotas_chat(),
        *rotas_modos(),
        *rotas_biblioteca(),
        *rotas_dossier(),
        *rotas_documento(),
        *rotas_modelos(),
    ]

    raiz_ui = Path(raiz_estaticos) if raiz_estaticos is not None else None
    tem_dist = caminho_dist(raiz_ui) is not None
    if not tem_dist:
        rotas.append(Route("/", raiz_placeholder, methods=["GET"]))

    app = Starlette(routes=rotas)
    app.state.caminho_sqlite = caminho
    app.state.motor_procura = motor_procura or motor_procura_sem_e2b
    app.state.com_e2b = com_e2b
    app.state.slot = slot or SlotPesado()
    app.state.raiz_modelos = (
        Path(raiz_modelos) if raiz_modelos is not None else None
    )
    app.state.forcar_estado_modelos = forcar_estado_modelos
    app.state.descarregar_modelo = descarregar_modelo

    for mount in montar_estaticos(raiz_ui):
        app.routes.append(mount)

    return app
