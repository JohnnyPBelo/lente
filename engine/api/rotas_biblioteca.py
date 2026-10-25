"""Rotas mínimas da biblioteca (HTTP-library-list / ingest)."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from engine.api.erros import PEDIDO_INVALIDO, URL_PRIVADA, resposta_erro
from engine.api.ids import doc_id
from engine.armazenamento.repositorio import abrir
from engine.ingestao import extrair
from engine.ingestao.indexar_minimo import indexar_texto_fts
from engine.ingestao.registo import registar_ficheiro
from engine.ingestao.ssrf import UrlRecusada, validar_url
from engine.ingestao.tipos import FicheiroInexistente, TipoNaoSuportado

_NOME_SEGURO = re.compile(r"[^A-Za-z0-9._\-]+")


def _ligacao(request: Request) -> sqlite3.Connection:
    return abrir(Path(request.app.state.caminho_sqlite))


def _pasta_uploads(request: Request) -> Path:
    configurada = getattr(request.app.state, "pasta_uploads", None)
    if configurada is not None:
        destino = Path(configurada)
    else:
        sqlite = Path(request.app.state.caminho_sqlite)
        destino = sqlite.parent / "biblioteca"
    destino.mkdir(parents=True, exist_ok=True)
    return destino


def _nome_seguro(nome: str | None) -> str:
    bruto = (nome or "upload.bin").strip() or "upload.bin"
    limpo = _NOME_SEGURO.sub("_", Path(bruto).name)
    return limpo[:180] or "upload.bin"


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


def _indexar_registo(ligacao: sqlite3.Connection, documento_id: int, caminho: Path) -> None:
    extraccao = extrair(caminho)
    indexar_texto_fts(
        ligacao,
        documento_id=documento_id,
        texto=extraccao.texto,
    )


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
        # URL pública: contrato mínimo (fila); ficheiros locais são o caminho feliz.
        return JSONResponse(
            {"documento_id": "doc_0", "estado": "na_fila"},
            status_code=202,
        )

    form = await request.form()
    ficheiro = form.get("ficheiros") or form.get("ficheiro") or form.get("file")
    if ficheiro is None:
        return resposta_erro(400, PEDIDO_INVALIDO, "ficheiro ou url obrigatório.")
    if not isinstance(ficheiro, UploadFile):
        return resposta_erro(400, PEDIDO_INVALIDO, "ficheiro inválido.")

    pasta = _pasta_uploads(request)
    nome = _nome_seguro(ficheiro.filename)
    destino = pasta / nome
    contador = 1
    while destino.exists():
        destino = pasta / f"{destino.stem}_{contador}{destino.suffix}"
        contador += 1

    dados = await ficheiro.read()
    destino.write_bytes(dados)

    ligacao = _ligacao(request)
    try:
        registo = registar_ficheiro(ligacao, destino)
        _indexar_registo(ligacao, registo.id, destino)
    except (TipoNaoSuportado, FicheiroInexistente) as exc:
        destino.unlink(missing_ok=True)
        return resposta_erro(400, PEDIDO_INVALIDO, str(exc))
    except Exception as exc:  # noqa: BLE001 — erro observável ao cliente
        return resposta_erro(400, PEDIDO_INVALIDO, str(exc) or "falha na ingestão")

    return JSONResponse(
        {"documento_id": doc_id(registo.id), "estado": "ok"},
        status_code=202,
    )


def rotas_biblioteca() -> list[Route]:
    return [
        Route("/library", listar_biblioteca, methods=["GET"]),
        Route("/library/ingest", ingerir_biblioteca, methods=["POST"]),
    ]
