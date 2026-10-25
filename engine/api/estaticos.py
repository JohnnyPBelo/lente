"""Montar apps/ui/dist quando o artefacto de build existir."""

from __future__ import annotations

from pathlib import Path

from starlette.routing import Mount
from starlette.staticfiles import StaticFiles


def caminho_dist(raiz: Path | None = None) -> Path | None:
    """Devolve o caminho de ``apps/ui/dist`` se existir e tiver conteúdo."""
    base = Path(raiz) if raiz is not None else Path.cwd()
    dist = base / "apps" / "ui" / "dist"
    if dist.is_dir() and any(dist.iterdir()):
        return dist
    return None


def montar_estaticos(raiz: Path | None = None) -> list[Mount]:
    """Rotas para servir a UI estática; lista vazia se ainda não há build."""
    dist = caminho_dist(raiz)
    if dist is None:
        return []
    return [
        Mount(
            "/",
            app=StaticFiles(directory=str(dist), html=True),
            name="ui",
        )
    ]
