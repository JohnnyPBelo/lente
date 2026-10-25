"""HTTP-reader-* e HTTP-chat-pin-excerpt (PLN-15)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from engine.api.erros import (
    CHAT_INEXISTENTE,
    DOCUMENTO_INEXISTENTE,
    PEDIDO_INVALIDO,
    resposta_erro,
)
from engine.api.ids import IdInvalido, analisar_chat, analisar_doc, doc_id, formatar, msg_id
from engine.armazenamento.repositorio import abrir

# Memória de teste / mínimo sem índice completo
_DOCS: dict[str, dict[str, Any]] = {}
_PAGINAS: dict[str, dict[str, Any]] = {}
_HIGHLIGHTS: dict[str, list[dict[str, Any]]] = {}
_FIXADOS: list[dict[str, Any]] = []


def reiniciar_documento_falso() -> None:
    _DOCS.clear()
    _PAGINAS.clear()
    _HIGHLIGHTS.clear()
    _FIXADOS.clear()


def semear_documento(
    doc: dict[str, Any],
    paginas: list[dict[str, Any]] | None = None,
    highlights: list[dict[str, Any]] | None = None,
) -> None:
    _DOCS[str(doc["id"])] = doc
    for p in paginas or []:
        _PAGINAS[f"{doc['id']}:{p['pagina']}"] = p
    _HIGHLIGHTS[str(doc["id"])] = list(highlights or [])


def _json(corpo: Any, *, status: int = 200) -> Response:
    return Response(
        json.dumps(corpo, ensure_ascii=False).encode("utf-8"),
        status_code=status,
        media_type="application/json",
    )


def _agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ligacao(request: Request) -> sqlite3.Connection | None:
    caminho = getattr(request.app.state, "caminho_sqlite", None)
    if caminho is None:
        return None
    return abrir(Path(caminho))


def _doc_numero(documento_id: str) -> int | None:
    try:
        return analisar_doc(documento_id)
    except Exception:
        return None


def _documento_existente(ligacao: sqlite3.Connection, documento_id: str) -> int | None:
    """Devolve o id numérico se existir na BD; nunca inventa linhas."""
    numero = _doc_numero(documento_id)
    if numero is None:
        return None
    existente = ligacao.execute(
        "SELECT id FROM documentos WHERE id = ?", (numero,)
    ).fetchone()
    if existente is None:
        return None
    return numero


def _garantir_conversa(ligacao: sqlite3.Connection, conversa_numero: int) -> None:
    existente = ligacao.execute(
        "SELECT id FROM conversas WHERE id = ?", (conversa_numero,)
    ).fetchone()
    if existente is not None:
        return
    momento = _agora()
    ligacao.execute(
        "INSERT INTO conversas (id, titulo, criado_em, actualizado_em, apagada) "
        "VALUES (?, '', ?, ?, 0)",
        (conversa_numero, momento, momento),
    )
    ligacao.commit()


def _garantir_mensagem(ligacao: sqlite3.Connection, conversa_numero: int) -> int:
    linha = ligacao.execute(
        "SELECT id FROM mensagens WHERE conversa_id = ? ORDER BY id DESC LIMIT 1",
        (conversa_numero,),
    ).fetchone()
    if linha is not None:
        return int(linha["id"])
    momento = _agora()
    cur = ligacao.execute(
        "INSERT INTO mensagens "
        "(conversa_id, papel, conteudo, criado_em) VALUES (?, 'utilizador', '', ?)",
        (conversa_numero, momento),
    )
    ligacao.commit()
    return int(cur.lastrowid)


async def http_documento(request: Request) -> Response:
    doc_id_param = request.path_params["documento_id"]
    if doc_id_param in _DOCS:
        return _json(_DOCS[doc_id_param])

    ligacao = _ligacao(request)
    if ligacao is None:
        return resposta_erro(
            404, DOCUMENTO_INEXISTENTE, "Documento não encontrado."
        )
    try:
        numero = analisar_doc(doc_id_param)
    except IdInvalido:
        return resposta_erro(400, PEDIDO_INVALIDO, "documento_id inválido")
    linha = ligacao.execute(
        "SELECT id, titulo, tipo, sha256, estado, paginas, sumario_json "
        "FROM documentos WHERE id = ?",
        (numero,),
    ).fetchone()
    if linha is None:
        return resposta_erro(
            404, DOCUMENTO_INEXISTENTE, "Documento não encontrado."
        )
    sumario: list[Any] = []
    if linha["sumario_json"]:
        try:
            bruto = json.loads(linha["sumario_json"])
            if isinstance(bruto, list):
                sumario = bruto
        except json.JSONDecodeError:
            sumario = []
    etiquetas = [
        r[0]
        for r in ligacao.execute(
            "SELECT e.nome FROM etiquetas e "
            "JOIN documento_etiquetas de ON de.etiqueta_id = e.id "
            "WHERE de.documento_id = ? ORDER BY e.nome",
            (numero,),
        ).fetchall()
    ]
    return _json(
        {
            "id": doc_id(int(linha["id"])),
            "titulo": linha["titulo"],
            "tipo": linha["tipo"] or "texto",
            "paginas": int(linha["paginas"] or 1),
            "hash_sha256": linha["sha256"],
            "desactualizado": linha["estado"] == "desactualizado",
            "sumario": sumario,
            "etiquetas": etiquetas,
        }
    )


async def http_pagina(request: Request) -> Response:
    doc_id_param = request.path_params["documento_id"]
    pagina = int(request.path_params["pagina"])
    chave = f"{doc_id_param}:{pagina}"
    if chave in _PAGINAS:
        return _json(_PAGINAS[chave])

    ligacao = _ligacao(request)
    if ligacao is None:
        return _json({"pagina": pagina, "texto": "", "largura": 595, "altura": 842})
    try:
        numero = analisar_doc(doc_id_param)
    except IdInvalido:
        return resposta_erro(400, PEDIDO_INVALIDO, "documento_id inválido")
    existe = ligacao.execute(
        "SELECT id FROM documentos WHERE id = ?", (numero,)
    ).fetchone()
    if existe is None:
        return resposta_erro(
            404, DOCUMENTO_INEXISTENTE, "Documento não encontrado."
        )
    # Preferir frases da página; senão concatenar blocos.
    frases = ligacao.execute(
        "SELECT texto FROM frases WHERE documento_id = ? AND (pagina = ? OR pagina IS NULL) "
        "ORDER BY ordem ASC, id ASC",
        (numero, pagina),
    ).fetchall()
    if frases:
        texto = "\n".join(str(f["texto"]) for f in frases)
    else:
        blocos = ligacao.execute(
            "SELECT texto FROM blocos WHERE documento_id = ? "
            "AND (pagina_inicio IS NULL OR pagina_inicio <= ?) "
            "AND (pagina_fim IS NULL OR pagina_fim >= ?) "
            "ORDER BY ordem ASC, id ASC",
            (numero, pagina, pagina),
        ).fetchall()
        texto = "\n\n".join(str(b["texto"]) for b in blocos)
    return _json(
        {"pagina": pagina, "texto": texto, "largura": 595, "altura": 842}
    )


async def http_highlights(request: Request) -> Response:
    doc_id_param = request.path_params["documento_id"]
    mensagem_id = request.query_params.get("mensagem_id")
    itens = list(_HIGHLIGHTS.get(doc_id_param, []))
    if mensagem_id:
        itens = [
            i
            for i in itens
            if not i.get("mensagem_id") or i.get("mensagem_id") == mensagem_id
        ]
    if itens:
        return _json({"itens": itens})

    ligacao = _ligacao(request)
    if ligacao is None:
        return _json({"itens": []})
    try:
        numero = analisar_doc(doc_id_param)
    except IdInvalido:
        return resposta_erro(400, PEDIDO_INVALIDO, "documento_id inválido")

    sql = (
        "SELECT c.id, c.mensagem_id, c.indice, c.trecho_literal, c.pagina, "
        "c.offset_inicio, c.offset_fim, c.caixas_json "
        "FROM citacoes c WHERE c.documento_id = ?"
    )
    params: list[Any] = [numero]
    if mensagem_id:
        from engine.api.ids import analisar as _analisar_id

        try:
            msg_num = _analisar_id(mensagem_id, "msg")
        except IdInvalido:
            return _json({"itens": []})
        sql += " AND c.mensagem_id = ?"
        params.append(msg_num)
    sql += " ORDER BY c.indice ASC, c.id ASC"
    linhas = ligacao.execute(sql, params).fetchall()
    saida = []
    for l in linhas:
        caixas: list[Any] = []
        if l["caixas_json"]:
            try:
                bruto = json.loads(l["caixas_json"])
                if isinstance(bruto, list):
                    caixas = bruto
            except json.JSONDecodeError:
                caixas = []
        saida.append(
            {
                "n": int(l["indice"]),
                "mensagem_id": msg_id(int(l["mensagem_id"])),
                "documento_id": doc_id_param,
                "pagina": l["pagina"] or 1,
                "texto": l["trecho_literal"],
                "offsets": {
                    "inicio": l["offset_inicio"] or 0,
                    "fim": l["offset_fim"] or 0,
                },
                "caixas": caixas,
            }
        )
    return _json({"itens": saida})


async def http_listar_fixados(request: Request) -> Response:
    chat_bruto = request.path_params["chat_id"]
    try:
        conversa_numero = analisar_chat(chat_bruto)
    except Exception:
        return resposta_erro(404, CHAT_INEXISTENTE, "Conversa não encontrada.")

    ligacao = _ligacao(request)
    if ligacao is None:
        itens = [f for f in _FIXADOS if f["chat_id"] == chat_bruto]
        return _json({"itens": itens})

    linhas = ligacao.execute(
        "SELECT id, documento_id, trecho_literal, ficheiro, pagina, "
        "offset_inicio, offset_fim "
        "FROM trechos_fixados WHERE conversa_id = ? ORDER BY id ASC",
        (conversa_numero,),
    ).fetchall()
    itens = [
        {
            "id": formatar("fix", int(l["id"])),
            "documento_id": doc_id(int(l["documento_id"])),
            "texto": l["trecho_literal"],
            "ficheiro": l["ficheiro"],
            "pagina": l["pagina"],
            "offsets": {
                "inicio": l["offset_inicio"],
                "fim": l["offset_fim"],
            },
        }
        for l in linhas
    ]
    return _json({"itens": itens})


async def http_fixar(request: Request) -> Response:
    chat_bruto = request.path_params["chat_id"]
    try:
        conversa_numero = analisar_chat(chat_bruto)
    except Exception:
        return resposta_erro(404, CHAT_INEXISTENTE, "Conversa não encontrada.")

    try:
        corpo = await request.json()
    except Exception:
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
    if not isinstance(corpo, dict) or not str(corpo.get("texto") or "").strip():
        return resposta_erro(400, PEDIDO_INVALIDO, "texto em falta")

    doc_bruto = corpo.get("documento_id")
    if not isinstance(doc_bruto, str):
        return resposta_erro(400, PEDIDO_INVALIDO, "documento_id em falta")

    offsets = corpo.get("offsets") or {}
    pagina = corpo.get("pagina")
    texto = str(corpo["texto"]).strip()
    ficheiro = str(corpo.get("ficheiro") or doc_bruto)

    ligacao = _ligacao(request)
    if ligacao is None:
        fix_id = f"fix_{len(_FIXADOS) + 1}"
        linha = {
            "id": fix_id,
            "chat_id": chat_bruto,
            "documento_id": doc_bruto,
            "pagina": pagina,
            "texto": texto,
            "offsets": offsets,
        }
        _FIXADOS.append(linha)
        return _json({"id": fix_id}, status=201)

    _garantir_conversa(ligacao, conversa_numero)

    doc_numero = _documento_existente(ligacao, doc_bruto)
    if doc_numero is None:
        return resposta_erro(
            404, DOCUMENTO_INEXISTENTE, "Documento não encontrado."
        )

    mensagem_numero = _garantir_mensagem(ligacao, conversa_numero)
    momento = _agora()
    cur = ligacao.execute(
        "INSERT INTO trechos_fixados "
        "(mensagem_id, conversa_id, documento_id, trecho_literal, ficheiro, "
        " pagina, offset_inicio, offset_fim, caixas_json, fixado_em) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            mensagem_numero,
            conversa_numero,
            doc_numero,
            texto,
            ficheiro,
            pagina,
            offsets.get("inicio"),
            offsets.get("fim"),
            json.dumps(corpo.get("caixas") or [], ensure_ascii=False),
            momento,
        ),
    )
    ligacao.commit()
    fix_numero = int(cur.lastrowid)
    fix_id = formatar("fix", fix_numero)
    _FIXADOS.append(
        {
            "id": fix_id,
            "chat_id": chat_bruto,
            "documento_id": doc_bruto,
            "pagina": pagina,
            "texto": texto,
            "offsets": offsets,
        }
    )
    return _json({"id": fix_id}, status=201)


def listar_fixados(chat_id: str) -> list[dict[str, Any]]:
    return [f for f in _FIXADOS if f["chat_id"] == chat_id]


def rotas_documento() -> list[Route]:
    return [
        Route("/documents/{documento_id}", http_documento, methods=["GET"]),
        Route(
            "/documents/{documento_id}/pages/{pagina}",
            http_pagina,
            methods=["GET"],
        ),
        Route(
            "/documents/{documento_id}/highlights",
            http_highlights,
            methods=["GET"],
        ),
        Route("/chats/{chat_id}/fixados", http_listar_fixados, methods=["GET"]),
        Route("/chats/{chat_id}/fixados", http_fixar, methods=["POST"]),
    ]
