"""HTTP-feedback — POST /feedback (Acertou / Corrigir / Descartar)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from engine.api.erros import PEDIDO_INVALIDO, resposta_erro
from engine.api.ids import IdInvalido, analisar_msg
from engine.armazenamento.repositorio import abrir
from engine.diario.escrever import registar_feedback as diario_feedback
from engine.feedback.registar import (
    registar_acertou,
    registar_corrigir,
    registar_descartar,
)

_ACCOES = frozenset({"acertou", "corrigir", "descartar"})


def _ligacao(request: Request) -> sqlite3.Connection:
    return abrir(Path(request.app.state.caminho_sqlite))


def _mensagem(ligacao: sqlite3.Connection, numero: int) -> sqlite3.Row | None:
    return ligacao.execute(
        "SELECT id, conversa_id, papel, lente, conteudo, meta_json "
        "FROM mensagens WHERE id = ?",
        (numero,),
    ).fetchone()


def _pergunta_anterior(ligacao: sqlite3.Connection, mensagem: sqlite3.Row) -> str:
    linha = ligacao.execute(
        "SELECT conteudo FROM mensagens "
        "WHERE conversa_id = ? AND id < ? AND papel = 'utilizador' "
        "ORDER BY id DESC LIMIT 1",
        (int(mensagem["conversa_id"]), int(mensagem["id"])),
    ).fetchone()
    if linha is None:
        return ""
    return str(linha["conteudo"] or "")


def _trechos_mostrados(ligacao: sqlite3.Connection, mensagem_id: int) -> list[str]:
    citacoes = ligacao.execute(
        "SELECT trecho_literal FROM citacoes "
        "WHERE mensagem_id = ? ORDER BY indice ASC, id ASC",
        (mensagem_id,),
    ).fetchall()
    if citacoes:
        return [str(c["trecho_literal"] or "") for c in citacoes if c["trecho_literal"]]

    linha = ligacao.execute(
        "SELECT meta_json FROM mensagens WHERE id = ?", (mensagem_id,)
    ).fetchone()
    if linha is None or not linha["meta_json"]:
        return []
    try:
        meta = json.loads(linha["meta_json"])
    except json.JSONDecodeError:
        return []
    saida: list[str] = []
    for ex in meta.get("excertos") or []:
        if isinstance(ex, dict) and str(ex.get("texto") or "").strip():
            saida.append(str(ex["texto"]).strip())
    return saida


def _textos_positivos(positivos: Any) -> list[str]:
    if not isinstance(positivos, list):
        return []
    textos: list[str] = []
    for item in positivos:
        if isinstance(item, str) and item.strip():
            textos.append(item.strip())
        elif isinstance(item, dict):
            texto = str(item.get("texto") or "").strip()
            if texto:
                textos.append(texto)
    return textos


async def http_feedback(request: Request) -> Response:
    if getattr(request.app.state, "caminho_sqlite", None) is None:
        return resposta_erro(400, PEDIDO_INVALIDO, "SQLite não configurado.")
    try:
        corpo = await request.json()
    except Exception:
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")
    if not isinstance(corpo, dict):
        return resposta_erro(400, PEDIDO_INVALIDO, "JSON inválido.")

    accao = corpo.get("accao")
    if accao not in _ACCOES:
        return resposta_erro(
            400,
            PEDIDO_INVALIDO,
            "accao deve ser acertou, corrigir ou descartar.",
        )

    msg_bruto = corpo.get("mensagem_id")
    if not isinstance(msg_bruto, str) or not msg_bruto.strip():
        return resposta_erro(400, PEDIDO_INVALIDO, "mensagem_id obrigatório.")
    try:
        mensagem_numero = analisar_msg(msg_bruto.strip())
    except IdInvalido:
        return resposta_erro(400, PEDIDO_INVALIDO, "mensagem_id inválido.")

    ligacao = _ligacao(request)
    mensagem = _mensagem(ligacao, mensagem_numero)
    if mensagem is None:
        return resposta_erro(404, PEDIDO_INVALIDO, "Mensagem inexistente.")

    lente = str(mensagem["lente"] or corpo.get("lente") or "investigar")
    pergunta = _pergunta_anterior(ligacao, mensagem)
    slot = getattr(request.app.state, "slot", None)

    if accao == "descartar":
        registar_descartar(
            ligacao,
            mensagem_id=mensagem_numero,
            pergunta=pergunta,
            trechos_mostrados=_trechos_mostrados(ligacao, mensagem_numero),
            lente=lente,
            slot=slot,
        )
    elif accao == "acertou":
        trechos = _trechos_mostrados(ligacao, mensagem_numero)
        registar_acertou(
            ligacao,
            mensagem_id=mensagem_numero,
            pergunta=pergunta,
            trechos_mostrados=trechos,
            lente=lente,
            slot=slot,
        )
    else:  # corrigir
        positivos = _textos_positivos(corpo.get("positivos"))
        if not positivos:
            return resposta_erro(
                400,
                PEDIDO_INVALIDO,
                "positivos obrigatório em corrigir.",
            )
        marcas = _trechos_mostrados(ligacao, mensagem_numero)
        # Uma selecção positiva por pedido; se vierem várias, junta-as.
        selecao = "\n".join(positivos)
        registar_corrigir(
            ligacao,
            mensagem_id=mensagem_numero,
            pergunta=pergunta,
            marcas_resposta=marcas,
            selecao=selecao,
            lente=lente,
            slot=slot,
        )

    diario_feedback(
        ligacao,
        {"mensagem_id": msg_bruto.strip(), "accao": accao},
    )

    # LoRA só com máquina livre — neste caminho imediato não agenda treino.
    return JSONResponse({"aceite": True, "treino_agendado": False}, status_code=202)


def rotas_feedback() -> list[Route]:
    return [Route("/feedback", http_feedback, methods=["POST"])]
