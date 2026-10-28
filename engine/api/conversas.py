"""CRUD mínimo de conversas e mensagens no SQLite."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from engine.api.ids import chat_id, msg_id


def _agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def titulo_api(titulo_bd: str | None) -> str | None:
    """Título vazio na BD expõe-se como ``null`` no contrato."""
    if titulo_bd is None or titulo_bd == "":
        return None
    return titulo_bd


def criar_conversa(ligacao: sqlite3.Connection, *, titulo: str | None = None) -> dict[str, Any]:
    momento = _agora()
    titulo_bd = "" if titulo is None else titulo
    cur = ligacao.execute(
        "INSERT INTO conversas (titulo, criado_em, actualizado_em, apagada) "
        "VALUES (?, ?, ?, 0)",
        (titulo_bd, momento, momento),
    )
    ligacao.commit()
    numero = int(cur.lastrowid)
    return {
        "id": chat_id(numero),
        "titulo": titulo_api(titulo_bd),
        "mensagens": [],
    }


def listar_conversas(ligacao: sqlite3.Connection) -> list[dict[str, Any]]:
    linhas = ligacao.execute(
        "SELECT id, titulo, actualizado_em FROM conversas "
        "WHERE apagada = 0 ORDER BY actualizado_em DESC, id DESC"
    ).fetchall()
    return [
        {
            "id": chat_id(int(linha["id"])),
            "titulo": titulo_api(linha["titulo"]),
            "actualizado_em": linha["actualizado_em"],
        }
        for linha in linhas
    ]


def obter_conversa(
    ligacao: sqlite3.Connection, numero: int
) -> dict[str, Any] | None:
    linha = ligacao.execute(
        "SELECT id, titulo FROM conversas WHERE id = ? AND apagada = 0",
        (numero,),
    ).fetchone()
    if linha is None:
        return None
    mensagens = ligacao.execute(
        "SELECT id, papel, conteudo, meta_json FROM mensagens "
        "WHERE conversa_id = ? ORDER BY id ASC",
        (numero,),
    ).fetchall()
    itens: list[dict[str, Any]] = []
    for m in mensagens:
        item: dict[str, Any] = {
            "id": msg_id(int(m["id"])),
            "papel": m["papel"],
        }
        if m["papel"] == "utilizador":
            item["texto"] = m["conteudo"]
        else:
            meta = json.loads(m["meta_json"] or "{}")
            if "frases" in meta:
                item["frases"] = meta["frases"]
            if "excertos" in meta:
                item["excertos"] = meta["excertos"]
            if "miniaturas" in meta:
                item["miniaturas"] = meta["miniaturas"]
            if "texto" in meta:
                item["texto"] = meta["texto"]
            elif m["conteudo"] and "frases" not in item:
                item["texto"] = m["conteudo"]
        itens.append(item)
    return {
        "id": chat_id(int(linha["id"])),
        "titulo": titulo_api(linha["titulo"]),
        "mensagens": itens,
    }


def renomear_conversa(
    ligacao: sqlite3.Connection, numero: int, titulo: str
) -> dict[str, Any] | None:
    existente = ligacao.execute(
        "SELECT id FROM conversas WHERE id = ? AND apagada = 0",
        (numero,),
    ).fetchone()
    if existente is None:
        return None
    momento = _agora()
    ligacao.execute(
        "UPDATE conversas SET titulo = ?, actualizado_em = ? WHERE id = ?",
        (titulo, momento, numero),
    )
    ligacao.commit()
    return {"id": chat_id(numero), "titulo": titulo}


def apagar_conversa(ligacao: sqlite3.Connection, numero: int) -> bool:
    cur = ligacao.execute(
        "UPDATE conversas SET apagada = 1, actualizado_em = ? "
        "WHERE id = ? AND apagada = 0",
        (_agora(), numero),
    )
    ligacao.commit()
    return cur.rowcount > 0


def conversa_sem_nome(ligacao: sqlite3.Connection, numero: int) -> bool:
    linha = ligacao.execute(
        "SELECT titulo FROM conversas WHERE id = ? AND apagada = 0",
        (numero,),
    ).fetchone()
    if linha is None:
        return False
    return titulo_api(linha["titulo"]) is None


def nomear_pela_primeira_procura(
    ligacao: sqlite3.Connection, numero: int, texto: str
) -> None:
    if not conversa_sem_nome(ligacao, numero):
        return
    ligacao.execute(
        "UPDATE conversas SET titulo = ?, actualizado_em = ? WHERE id = ?",
        (texto.strip(), _agora(), numero),
    )
    ligacao.commit()


def gravar_turno_procura(
    ligacao: sqlite3.Connection,
    *,
    conversa_numero: int,
    texto_utilizador: str,
    lente: str | None,
    resultado: dict[str, Any],
) -> str:
    """Grava mensagem do utilizador + assistente; devolve msg_id do assistente."""
    momento = _agora()
    ligacao.execute(
        "INSERT INTO mensagens "
        "(conversa_id, papel, modo, lente, conteudo, meta_json, criado_em) "
        "VALUES (?, 'utilizador', 'procurar', ?, ?, NULL, ?)",
        (conversa_numero, lente, texto_utilizador, momento),
    )
    meta = {
        "frases": [f.get("texto") for f in resultado.get("frases") or []],
        "excertos": [
            {
                "n": e.get("n"),
                "documento_id": e.get("documento_id"),
                "pagina": e.get("pagina"),
                "texto": e.get("texto"),
            }
            for e in resultado.get("excertos") or []
        ],
        "miniaturas": list(resultado.get("miniaturas") or []),
    }
    conteudo = "\n".join(meta["frases"]) if meta["frases"] else ""
    cur = ligacao.execute(
        "INSERT INTO mensagens "
        "(conversa_id, papel, modo, lente, conteudo, meta_json, criado_em) "
        "VALUES (?, 'assistente', 'procurar', ?, ?, ?, ?)",
        (conversa_numero, lente, conteudo, json.dumps(meta, ensure_ascii=False), momento),
    )
    mensagem_numero = int(cur.lastrowid)
    for ex in resultado.get("excertos") or []:
        doc_bruto = ex.get("documento_id")
        if not isinstance(doc_bruto, str) or not doc_bruto.startswith("doc_"):
            continue
        try:
            doc_num = int(doc_bruto.split("_", 1)[1])
        except ValueError:
            continue
        offsets = ex.get("offsets") or {}
        doc_row = ligacao.execute(
            "SELECT caminho, sha256 FROM documentos WHERE id = ?",
            (doc_num,),
        ).fetchone()
        caminho = ""
        sha_doc: str | None = None
        if doc_row is not None:
            caminho = str(doc_row[0] or "")
            sha_doc = str(doc_row[1]) if doc_row[1] else None
        ligacao.execute(
            "INSERT INTO citacoes "
            "(mensagem_id, documento_id, frase_id, indice, trecho_literal, "
            " ficheiro, pagina, offset_inicio, offset_fim, caixas_json, "
            " pontuacao_juiz, sha256_ficheiro) "
            "VALUES (?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                mensagem_numero,
                doc_num,
                int(ex.get("n") or 0),
                ex.get("texto") or "",
                caminho,
                ex.get("pagina"),
                offsets.get("inicio"),
                offsets.get("fim"),
                json.dumps(ex.get("caixas") or [], ensure_ascii=False),
                ex.get("score_juiz"),
                sha_doc,
            ),
        )
    ligacao.execute(
        "UPDATE conversas SET actualizado_em = ? WHERE id = ?",
        (momento, conversa_numero),
    )
    ligacao.commit()
    return msg_id(mensagem_numero)
