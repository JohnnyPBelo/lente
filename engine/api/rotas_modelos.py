"""HTTP-models-status / guidance / download — respostas honestas (#54)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from engine.runtime.pesos import estado_modelos, orientar_falta

DownloadFn = Callable[[str], dict[str, Any]]


def _raiz_modelos(request: Request) -> Path | None:
    valor = getattr(request.app.state, "raiz_modelos", None)
    return Path(valor) if valor is not None else None


def _forcar(request: Request) -> dict[str, Any] | None:
    return getattr(request.app.state, "forcar_estado_modelos", None)


async def models_status(request: Request) -> JSONResponse:
    return JSONResponse(
        estado_modelos(_raiz_modelos(request), forcar=_forcar(request))
    )


async def models_guidance(request: Request) -> JSONResponse:
    return JSONResponse(
        orientar_falta(_raiz_modelos(request), forcar=_forcar(request))
    )


async def models_download(request: Request) -> JSONResponse:
    """POST /models/download — só ``a_descarregar`` se houver downloader real."""
    corpo = await request.json()
    modelo = str(corpo.get("modelo", "")).strip()
    if modelo not in {"embedding", "juiz", "escritor"}:
        return JSONResponse(
            {"erro": "pedido_invalido", "mensagem": "modelo desconhecido"},
            status_code=400,
        )

    raiz = _raiz_modelos(request)
    # Já pronto: não inventar download.
    if raiz is not None:
        actual = estado_modelos(raiz, forcar=_forcar(request)).get(modelo, {})
        if actual.get("estado") == "pronto":
            return JSONResponse(
                {
                    "estado": "pronto",
                    "modelo": modelo,
                    "caminho": actual.get("caminho"),
                },
                status_code=200,
            )

    downloader: DownloadFn | None = getattr(
        request.app.state, "descarregar_modelo", None
    )
    if downloader is not None:
        resultado = downloader(modelo)
        codigo = int(resultado.pop("http_status", 202))
        return JSONResponse(resultado, status_code=codigo)

    # Sem downloader: orientação honesta — Gemma = licença; Apache = em falta.
    estado_forcar = "erro_licenca" if modelo == "escritor" else "em_falta"
    guia = orientar_falta(
        raiz,
        forcar={modelo: estado_forcar},  # type: ignore[dict-item]
    )
    guia["erro"] = estado_forcar
    return JSONResponse(guia, status_code=409)


def rotas_modelos() -> list[Route]:
    return [
        Route("/models/status", models_status, methods=["GET"]),
        Route("/models/guidance", models_guidance, methods=["GET"]),
        Route("/models/download", models_download, methods=["POST"]),
    ]
