"""Entrypoint ``lente``: migrações → registo de pesos → escuta 127.0.0.1:4317."""

from __future__ import annotations

import argparse
import sys
import threading
from pathlib import Path
from typing import Any, Sequence

from engine.api.app import criar_app
from engine.api.bind import HOST_OMISSAO, PORTA_OMISSAO
from engine.api.servidor import ServidorLocal, arrancar_servidor
from engine.armazenamento.caminho import caminho_sqlite, raiz_projecto
from engine.armazenamento.repositorio import abrir
from engine.runtime.piso import PisoInsuficiente, verificar_piso


def _parse_argv(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="lente",
        description=(
            "Sobe a Lente num só processo: migrações, pesos em models/ "
            f"e HTTP em {HOST_OMISSAO}:{PORTA_OMISSAO}."
        ),
    )
    parser.add_argument(
        "--host",
        default=HOST_OMISSAO,
        help=f"Só loopback (omissão: {HOST_OMISSAO})",
    )
    parser.add_argument(
        "--porta",
        type=int,
        default=PORTA_OMISSAO,
        help=f"Porto HTTP (omissão: {PORTA_OMISSAO})",
    )
    parser.add_argument(
        "--raiz",
        type=Path,
        default=None,
        help="Raiz do projecto (omissão: detectada)",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=None,
        help="Directório data/ (omissão: <raiz>/data)",
    )
    parser.add_argument(
        "--models",
        type=Path,
        default=None,
        help="Directório models/ (omissão: <raiz>/models)",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def preparar(
    *,
    raiz: Path | None = None,
    pasta_data: Path | None = None,
    pasta_modelos: Path | None = None,
) -> dict[str, Any]:
    """Aplica migrações e regista o estado dos pesos; não escuta ainda."""
    verificar_piso()
    base = raiz if raiz is not None else raiz_projecto()
    data = pasta_data if pasta_data is not None else base / "data"
    modelos = pasta_modelos if pasta_modelos is not None else base / "models"
    data.mkdir(parents=True, exist_ok=True)
    modelos.mkdir(parents=True, exist_ok=True)

    sqlite = data / "lente.sqlite" if pasta_data is not None else caminho_sqlite(base)
    abrir(sqlite)

    from engine.runtime.pesos import estado_modelos, orientar_falta

    estado = estado_modelos(modelos)
    orientacao = orientar_falta(modelos)
    return {
        "raiz": base,
        "sqlite": sqlite,
        "modelos": modelos,
        "estado_modelos": estado,
        "orientacao": orientacao,
    }


def arrancar(
    *,
    host: str = HOST_OMISSAO,
    porta: int = PORTA_OMISSAO,
    raiz: Path | None = None,
    pasta_data: Path | None = None,
    pasta_modelos: Path | None = None,
    bloquear: bool = True,
    app: Any | None = None,
) -> ServidorLocal:
    """Prepara o runtime e escuta em ``host:porta``.

    Com ``bloquear=False`` devolve o handle (útil em testes). Sem pesos E2B
    o processo **não** termina — a app abre na mesma.
    """
    ctx = preparar(raiz=raiz, pasta_data=pasta_data, pasta_modelos=pasta_modelos)
    aplicacao = app or criar_app(
        caminho_sqlite=ctx["sqlite"],
        raiz_modelos=ctx["modelos"],
        raiz_estaticos=ctx["raiz"],
    )
    servidor = arrancar_servidor(host=host, porta=porta, app=aplicacao)
    if bloquear:
        try:
            while True:
                threading.Event().wait(3600)
        except KeyboardInterrupt:
            servidor.parar()
    return servidor


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada do comando ``lente``."""
    try:
        args = _parse_argv(argv)
        arrancar(
            host=args.host,
            porta=args.porta,
            raiz=args.raiz,
            pasta_data=args.data,
            pasta_modelos=args.models,
            bloquear=True,
        )
    except PisoInsuficiente as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 — CLI devolve código, não stack
        print(f"lente: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
