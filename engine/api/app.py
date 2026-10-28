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
from engine.api.rotas_feedback import rotas_feedback
from engine.api.rotas_modelos import rotas_modelos
from engine.api.rotas_modos import rotas_modos
from engine.armazenamento.repositorio import abrir
from engine.escalonador.slot import SlotPesado
from engine.pesquisa.limiar import estado_limiar, limiar_visivel
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
    limiar = estado_limiar()
    return JSONResponse(
        {
            "ok": True,
            "versao": VERSAO,
            "modelos": modelos,
            "disco_data_mb": disco,
            "procura": procura,
            "limiar": limiar_visivel(),
            "platt_activo": limiar.platt_activo,
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
        *rotas_feedback(),
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
    _ligar_confronto(app, raiz_m)

    for mount in montar_estaticos(raiz_ui):
        app.routes.append(mount)

    return app


def _ligar_confronto(app: Starlette, raiz_modelos: Path | None) -> None:
    """Liga juiz + embedding ao HTTP-confront (issue #76).

    Sem pesos: deixa ``None`` e ``confrontar`` cai no Jaccard lexical honesto.
    Com pesos: cosseno 256d + σ(score ONNX) nas duas direcções.
    """
    if raiz_modelos is None:
        return

    from engine.runtime.pesos import estado_modelos

    estado = estado_modelos(raiz_modelos)
    tem_juiz = estado.get("juiz", {}).get("estado") == "pronto"
    tem_emb = estado.get("embedding", {}).get("estado") == "pronto"
    if not tem_juiz and not tem_emb:
        return

    cache: dict[str, Any] = {
        "juiz": None,
        "emb": None,
        "falha_juiz": False,
        "falha_emb": False,
    }
    raiz = raiz_modelos

    def _sessao_juiz() -> Any | None:
        if not tem_juiz or cache["falha_juiz"]:
            return None
        if cache["juiz"] is None:
            try:
                from engine.juiz.carregar import carregar_sessao

                cache["juiz"] = carregar_sessao(raiz_modelos=raiz)
            except Exception:  # noqa: BLE001 — degrada a Jaccard
                cache["falha_juiz"] = True
                return None
        return cache["juiz"]

    def _sessao_emb() -> Any | None:
        if not tem_emb or cache["falha_emb"]:
            return None
        if cache["emb"] is None:
            try:
                from engine.embeddings.carregar import carregar_modelo

                cache["emb"] = carregar_modelo(raiz_modelos=raiz, dispositivo="cpu")
            except Exception:  # noqa: BLE001 — degrada a Jaccard
                cache["falha_emb"] = True
                return None
        return cache["emb"]

    def _sigmoide(x: float) -> float:
        import math

        if x >= 0:
            z = math.exp(-x)
            return 1.0 / (1.0 + z)
        z = math.exp(x)
        return z / (1.0 + z)

    def _jaccard(x: str, y: str) -> float:
        ax = {t.lower() for t in x.split() if t}
        by = {t.lower() for t in y.split() if t}
        if not ax or not by:
            return 0.0
        return len(ax & by) / len(ax | by)

    def pontuar(a: str, b: str) -> float:
        sessao = _sessao_juiz()
        if sessao is None:
            return _jaccard(a, b)
        try:
            bruto = float(sessao.avaliar(a, [b])[0])
            return _sigmoide(bruto)
        except Exception:  # noqa: BLE001
            return _jaccard(a, b)

    def cosseno(a: str, b: str) -> float:
        sessao = _sessao_emb()
        if sessao is None:
            return _jaccard(a, b)
        try:
            from engine.embeddings.carregar import embutir

            va = embutir(a, sessao=sessao)
            vb = embutir(b, sessao=sessao)
            return float(
                sum(float(x) * float(y) for x, y in zip(va, vb, strict=True))
            )
        except Exception:  # noqa: BLE001
            return _jaccard(a, b)

    if tem_juiz:
        app.state.pontuar_confronto = pontuar
    if tem_emb:
        app.state.cosseno_confronto = cosseno
