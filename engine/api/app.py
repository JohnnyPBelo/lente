"""Aplicação ASGI Starlette: health, chat, procura, biblioteca, estáticos."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from engine.api.estaticos import caminho_dist, montar_estaticos
from engine.api.motor import (
    escritor_pronto,
    selecionar_motor_procura,
)
from engine.api.rotas_alertas import rotas_alertas
from engine.api.rotas_backup import rotas_backup
from engine.api.rotas_biblioteca import rotas_biblioteca
from engine.api.rotas_chat import rotas_chat
from engine.api.rotas_correcoes import rotas_correcoes
from engine.api.rotas_documento import rotas_documento
from engine.api.rotas_dossier import rotas_dossier
from engine.api.rotas_modelos import rotas_modelos
from engine.api.rotas_modos import rotas_modos
from engine.armazenamento.repositorio import abrir
from engine.escalonador.slot import SlotPesado
from engine.pesquisa.limiar import limiar_visivel
from engine.runtime.descarregar import criar_descarregador
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
    motor = getattr(request.app.state, "motor_procura", None)
    procura = getattr(motor, "modo", None) or (
        "pipeline"
        if modelos.get("juiz") == "pronto"
        else "fts_degradado"
    )
    disco = 0
    caminho = getattr(request.app.state, "caminho_sqlite", None)
    if caminho is not None:
        ficheiro = Path(caminho)
        if ficheiro.is_file():
            disco = (
                max(1, ficheiro.stat().st_size // (1024 * 1024))
                if ficheiro.stat().st_size >= 1024 * 1024
                else 0
            )
    return JSONResponse(
        {
            "ok": True,
            "versao": VERSAO,
            "modelos": modelos,
            "disco_data_mb": disco,
            "procura": procura,
            "limiar": limiar_visivel(),
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
    pasta_uploads: Path | str | None = None,
    pasta_miniaturas: Path | str | None = None,
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
        *rotas_alertas(),
        *rotas_correcoes(),
        *rotas_backup(),
    ]

    raiz_ui = Path(raiz_estaticos) if raiz_estaticos is not None else None
    tem_dist = caminho_dist(raiz_ui) is not None
    if not tem_dist:
        rotas.append(Route("/", raiz_placeholder, methods=["GET"]))

    raiz_m = Path(raiz_modelos) if raiz_modelos is not None else None
    if motor_procura is not None:
        motor = motor_procura
    else:
        motor = selecionar_motor_procura(caminho, raiz_modelos=raiz_m)

    # E2B só se o GGUF estiver em disco (ou o caller forçar True com double).
    e2b_activo = com_e2b or escritor_pronto(raiz_m)

    uploads = Path(pasta_uploads) if pasta_uploads is not None else None
    if uploads is None and caminho is not None:
        uploads = caminho.parent / "biblioteca"

    thumbs = Path(pasta_miniaturas) if pasta_miniaturas is not None else None
    if thumbs is None and caminho is not None:
        thumbs = caminho.parent / "miniaturas"
    if thumbs is not None:
        thumbs.mkdir(parents=True, exist_ok=True)
        rotas.append(
            Mount(
                "/media/thumbs",
                app=StaticFiles(directory=str(thumbs)),
                name="miniaturas",
            )
        )

    downloader = descarregar_modelo
    if downloader is None and raiz_m is not None:
        downloader = criar_descarregador(raiz_m)

    app = Starlette(routes=rotas)
    app.state.caminho_sqlite = caminho
    app.state.motor_procura = motor
    app.state.com_e2b = e2b_activo
    app.state.slot = slot or SlotPesado()
    app.state.raiz_modelos = raiz_m
    app.state.pasta_uploads = uploads
    app.state.pasta_miniaturas = thumbs
    app.state.pasta_data = caminho.parent if caminho is not None else None
    app.state.forcar_estado_modelos = forcar_estado_modelos
    app.state.descarregar_modelo = downloader

    for mount in montar_estaticos(raiz_ui):
        app.routes.append(mount)

    return app
