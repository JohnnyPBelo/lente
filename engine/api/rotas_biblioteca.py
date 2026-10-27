"""Rotas mínimas da biblioteca (HTTP-library-list / ingest)."""

from __future__ import annotations

import hashlib
import re
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from engine.api.erros import PEDIDO_INVALIDO, URL_PRIVADA, resposta_erro
from engine.api.ids import IdInvalido, analisar_doc, doc_id
from engine.armazenamento.repositorio import abrir
from engine.biblioteca.etiquetas import definir_etiquetas
from engine.ingestao import extrair
from engine.ingestao.indexar_minimo import indexar_texto_fts
from engine.ingestao.registo import registar_ficheiro
from engine.ingestao.ssrf import UrlRecusada
from engine.ingestao.tipos import FicheiroInexistente, TipoNaoSuportado
from engine.ingestao.url import ingestir_url

_NOME_SEGURO = re.compile(r"[^A-Za-z0-9._\-]+")
# Teto local: evita DoS de RAM/disco em multipart (issue #49).
LIMITE_UPLOAD_BYTES = 50 * 1024 * 1024
_CHUNK = 64 * 1024


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


def _pasta_miniaturas(request: Request) -> Path:
    configurada = getattr(request.app.state, "pasta_miniaturas", None)
    if configurada is not None:
        destino = Path(configurada)
    else:
        sqlite = Path(request.app.state.caminho_sqlite)
        destino = sqlite.parent / "miniaturas"
    destino.mkdir(parents=True, exist_ok=True)
    return destino


def _nome_seguro(nome: str | None) -> str:
    bruto = (nome or "upload.bin").strip() or "upload.bin"
    limpo = _NOME_SEGURO.sub("_", Path(bruto).name)
    return limpo[:180] or "upload.bin"


def _destino_url(pasta: Path, url: str) -> Path:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    analisado = urlparse(url)
    base = Path(analisado.path or "").name or "artigo"
    stem = _nome_seguro(Path(base).stem) or "artigo"
    return pasta / f"url_{digest}_{stem}.txt"


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


def _indexar_registo(
    ligacao: sqlite3.Connection,
    documento_id: int,
    caminho: Path,
    pasta_miniaturas: Path,
    *,
    raiz_modelos: Path | None = None,
) -> None:
    extraccao = extrair(caminho)
    indexar_texto_fts(
        ligacao,
        documento_id=documento_id,
        texto=extraccao.texto,
        pasta_miniaturas=pasta_miniaturas,
    )
    # Com EmbeddingGemma em disco, grava vectores 256d (cosseno exacto).
    if raiz_modelos is not None:
        titulo: str | None = None
        if extraccao.titulos:
            primeiro = extraccao.titulos[0].get("titulo")
            if isinstance(primeiro, str) and primeiro.strip():
                titulo = primeiro.strip()
        _tentar_vectores(
            ligacao,
            documento_id=documento_id,
            texto=extraccao.texto,
            titulo=titulo,
            raiz_modelos=raiz_modelos,
        )


def _tentar_vectores(
    ligacao: sqlite3.Connection,
    *,
    documento_id: int,
    texto: str,
    titulo: str | None,
    raiz_modelos: Path,
) -> None:
    from engine.api.motor import embedding_pronto
    from engine.embeddings.carregar import carregar_modelo, embutir
    from engine.embeddings.prefixos import prefixo_documento
    from engine.pesquisa.vec import guardar_vector

    if not embedding_pronto(raiz_modelos):
        return
    corpo = (texto or "").strip()
    if not corpo:
        return
    try:
        sessao = carregar_modelo(raiz_modelos=raiz_modelos, dispositivo="cpu")
        linha = ligacao.execute(
            "SELECT id, hash_id FROM blocos WHERE documento_id = ? ORDER BY id",
            (documento_id,),
        ).fetchall()
        for bloco in linha:
            bloco_id = int(bloco["id"])
            hash_id = int(bloco["hash_id"])
            entrada = prefixo_documento(titulo, str(
                ligacao.execute(
                    "SELECT texto FROM blocos WHERE id = ?", (bloco_id,)
                ).fetchone()["texto"]
            ))
            vector = embutir(entrada, sessao=sessao)
            guardar_vector(
                ligacao,
                bloco_id=bloco_id,
                hash_id=hash_id,
                vector=vector,
            )
    except Exception:
        # Indexação FTS já ficou; vectores são opcionais.
        return


async def ingerir_biblioteca(request: Request) -> Response:
    content_type = (request.headers.get("content-type") or "").lower()
    pasta = _pasta_uploads(request)
    thumbs = _pasta_miniaturas(request)

    if "application/json" in content_type:
        try:
            corpo = await request.json()
        except Exception:
            return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
        url = corpo.get("url") if isinstance(corpo, dict) else None
        if not isinstance(url, str) or not url.strip():
            return resposta_erro(400, PEDIDO_INVALIDO, "url obrigatória.")
        url_limpa = url.strip()
        destino = _destino_url(pasta, url_limpa)
        ligacao = _ligacao(request)
        try:
            registo = ingestir_url(ligacao, url_limpa, destino)
            raiz_m = getattr(request.app.state, "raiz_modelos", None)
            _indexar_registo(
                ligacao,
                registo.id,
                Path(registo.caminho),
                thumbs,
                raiz_modelos=Path(raiz_m) if raiz_m is not None else None,
            )
        except UrlRecusada:
            return resposta_erro(
                400,
                URL_PRIVADA,
                "Endereço privado recusado.",
            )
        except Exception as exc:  # noqa: BLE001 — erro observável ao cliente
            return resposta_erro(400, PEDIDO_INVALIDO, str(exc) or "falha na ingestão")
        return JSONResponse(
            {"documento_id": doc_id(registo.id), "estado": "ok"},
            status_code=202,
        )

    form = await request.form()
    ficheiro = form.get("ficheiros") or form.get("ficheiro") or form.get("file")
    if ficheiro is None:
        return resposta_erro(400, PEDIDO_INVALIDO, "ficheiro ou url obrigatório.")
    if not isinstance(ficheiro, UploadFile):
        return resposta_erro(400, PEDIDO_INVALIDO, "ficheiro inválido.")

    nome = _nome_seguro(ficheiro.filename)
    destino = pasta / nome
    contador = 1
    while destino.exists():
        destino = pasta / f"{destino.stem}_{contador}{destino.suffix}"
        contador += 1

    total = 0
    try:
        with destino.open("wb") as saida:
            while True:
                pedaco = await ficheiro.read(_CHUNK)
                if not pedaco:
                    break
                total += len(pedaco)
                if total > LIMITE_UPLOAD_BYTES:
                    saida.close()
                    destino.unlink(missing_ok=True)
                    return resposta_erro(
                        413,
                        PEDIDO_INVALIDO,
                        "Ficheiro demasiado grande.",
                    )
                saida.write(pedaco)
    except Exception:
        destino.unlink(missing_ok=True)
        raise

    ligacao = _ligacao(request)
    try:
        registo = registar_ficheiro(ligacao, destino)
        raiz_m = getattr(request.app.state, "raiz_modelos", None)
        _indexar_registo(
            ligacao,
            registo.id,
            destino,
            thumbs,
            raiz_modelos=Path(raiz_m) if raiz_m is not None else None,
        )
    except (TipoNaoSuportado, FicheiroInexistente) as exc:
        destino.unlink(missing_ok=True)
        return resposta_erro(400, PEDIDO_INVALIDO, str(exc))
    except Exception as exc:  # noqa: BLE001 — erro observável ao cliente
        return resposta_erro(400, PEDIDO_INVALIDO, str(exc) or "falha na ingestão")

    return JSONResponse(
        {"documento_id": doc_id(registo.id), "estado": "ok"},
        status_code=202,
    )


async def etiquetar_documento(request: Request) -> Response:
    """PUT /documents/{documento_id}/tags — etiquetas manuais."""
    bruto = request.path_params.get("documento_id", "")
    try:
        numero = analisar_doc(str(bruto))
    except IdInvalido:
        return resposta_erro(400, PEDIDO_INVALIDO, "documento_id inválido.")
    try:
        corpo = await request.json()
    except Exception:
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
    if not isinstance(corpo, dict):
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
    nomes = corpo.get("etiquetas")
    if not isinstance(nomes, list) or not all(isinstance(x, str) for x in nomes):
        return resposta_erro(400, PEDIDO_INVALIDO, "etiquetas deve ser lista de strings.")

    ligacao = _ligacao(request)
    existente = ligacao.execute(
        "SELECT id FROM documentos WHERE id = ?", (numero,)
    ).fetchone()
    if existente is None:
        return resposta_erro(404, PEDIDO_INVALIDO, "Documento inexistente.")
    finais = definir_etiquetas(ligacao, numero, list(nomes))
    return JSONResponse({"id": doc_id(numero), "etiquetas": finais})


def rotas_biblioteca() -> list[Route]:
    return [
        Route("/library", listar_biblioteca, methods=["GET"]),
        Route("/library/ingest", ingerir_biblioteca, methods=["POST"]),
        Route(
            "/documents/{documento_id}/tags",
            etiquetar_documento,
            methods=["PUT"],
        ),
    ]
