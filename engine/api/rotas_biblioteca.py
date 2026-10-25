"""Rotas mínimas da biblioteca (HTTP-library-list / ingest)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from engine.api.erros import PEDIDO_INVALIDO, URL_PRIVADA, resposta_erro
from engine.api.ids import doc_id
from engine.armazenamento.repositorio import abrir

from engine.ingestao.ssrf import UrlRecusada, validar_url


def _ligacao(request: Request) -> sqlite3.Connection:
    return abrir(Path(request.app.state.caminho_sqlite))


async def listar_biblioteca(request: Request) -> Response:
    limite_bruto = request.query_params.get("limite", "50")
    try:
        limite = max(1, min(200, int(limite_bruto)))
    except ValueError:
        limite = 50
    etiqueta = request.query_params.get("etiqueta")

    ligacao = _ligacao(request)
    if etiqueta:
        linhas = ligacao.execute(
            "SELECT d.id, d.titulo, d.tipo_sugerido, d.estado "
            "FROM documentos d "
            "JOIN documento_etiquetas de ON de.documento_id = d.id "
            "JOIN etiquetas e ON e.id = de.etiqueta_id "
            "WHERE e.nome = ? "
            "ORDER BY d.id DESC LIMIT ?",
            (etiqueta, limite),
        ).fetchall()
    else:
        linhas = ligacao.execute(
            "SELECT id, titulo, tipo_sugerido, estado "
            "FROM documentos ORDER BY id DESC LIMIT ?",
            (limite,),
        ).fetchall()

    itens = []
    for linha in linhas:
        etiquetas = [
            r[0]
            for r in ligacao.execute(
                "SELECT e.nome FROM etiquetas e "
                "JOIN documento_etiquetas de ON de.etiqueta_id = e.id "
                "WHERE de.documento_id = ? ORDER BY e.nome",
                (linha["id"],),
            ).fetchall()
        ]
        itens.append(
            {
                "id": doc_id(int(linha["id"])),
                "titulo": linha["titulo"],
                "etiquetas": etiquetas,
                "desactualizado": linha["estado"] == "desactualizado",
                "tipo_sugerido": linha["tipo_sugerido"],
            }
        )
    return JSONResponse({"itens": itens, "cursor_seguinte": None})


async def ingerir_biblioteca(request: Request) -> Response:
    content_type = (request.headers.get("content-type") or "").lower()
    if "application/json" in content_type:
        try:
            corpo = await request.json()
        except Exception:
            return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
        url = corpo.get("url") if isinstance(corpo, dict) else None
        if not isinstance(url, str) or not url.strip():
            return resposta_erro(400, PEDIDO_INVALIDO, "url obrigatória.")
        try:
            validar_url(url.strip())
        except UrlRecusada:
            return resposta_erro(
                400,
                URL_PRIVADA,
                "Endereço privado recusado.",
            )
        # Enfileirar fica para o dono da ingestão; aqui só o contrato mínimo
        return JSONResponse(
            {"documento_id": "doc_0", "estado": "na_fila"},
            status_code=202,
        )

    # Multipart: aceite mínimo sem processar bytes (PLN-02+ tratam o ficheiro)
    form = await request.form()
    ficheiro = form.get("ficheiros") or form.get("ficheiro") or form.get("file")
    if ficheiro is None:
        return resposta_erro(400, PEDIDO_INVALIDO, "ficheiro ou url obrigatório.")
    return JSONResponse(
        {"documento_id": "doc_0", "estado": "na_fila"},
        status_code=202,
    )


def rotas_biblioteca() -> list[Route]:
    return [
        Route("/library", listar_biblioteca, methods=["GET"]),
        Route("/library/ingest", ingerir_biblioteca, methods=["POST"]),
    ]
