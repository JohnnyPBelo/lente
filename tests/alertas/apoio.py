"""Helpers sintéticos para testes de alertas."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from engine.armazenamento.ligacao import abrir_ligacao
from engine.armazenamento.migracoes import aplicar_migracoes


MOMENTO = "2026-01-01T00:00:00Z"


def ligacao_migrada(caminho: Path) -> sqlite3.Connection:
    aplicar_migracoes(caminho)
    return abrir_ligacao(caminho)


def inserir_documento(
    ligacao: sqlite3.Connection,
    *,
    caminho: str = "/tmp/doc-alerta.txt",
    titulo: str = "Doc alerta",
    miniatura: str | None = "/tmp/mini-alerta.png",
    estado: str = "ok",
) -> int:
    cur = ligacao.execute(
        "INSERT INTO documentos ("
        "caminho, titulo, tipo, sha256, estado, miniatura_caminho, "
        "criado_em, actualizado_em, indexado_em"
        ") VALUES (?, ?, 'txt', 'abc', ?, ?, ?, ?, ?)",
        (caminho, titulo, estado, miniatura, MOMENTO, MOMENTO, MOMENTO),
    )
    documento_id = int(cur.lastrowid)
    ligacao.execute(
        "INSERT INTO documento_hashes "
        "(documento_id, sha256, visto_em, activa) VALUES (?, 'abc', ?, 1)",
        (documento_id, MOMENTO),
    )
    hash_id = int(ligacao.execute("SELECT last_insert_rowid()").fetchone()[0])
    ligacao.execute(
        "INSERT INTO blocos ("
        "documento_id, hash_id, ordem, texto, "
        "offset_inicio, offset_fim, tokens_aprox"
        ") VALUES (?, ?, 0, 'bloco', 0, 5, 1)",
        (documento_id, hash_id),
    )
    bloco_id = int(ligacao.execute("SELECT last_insert_rowid()").fetchone()[0])
    return documento_id if bloco_id else documento_id


def inserir_frase(
    ligacao: sqlite3.Connection,
    documento_id: int,
    texto: str,
    *,
    ordem: int = 0,
) -> int:
    bloco = ligacao.execute(
        "SELECT id FROM blocos WHERE documento_id = ? ORDER BY ordem LIMIT 1",
        (documento_id,),
    ).fetchone()
    if bloco is None:
        raise RuntimeError("documento sem bloco")
    cur = ligacao.execute(
        "INSERT INTO frases ("
        "bloco_id, documento_id, pagina, texto, "
        "offset_inicio, offset_fim, ordem"
        ") VALUES (?, ?, 1, ?, 0, ?, ?)",
        (bloco["id"], documento_id, texto, len(texto), ordem),
    )
    return int(cur.lastrowid)


def mensagens_do_fio(
    ligacao: sqlite3.Connection, conversa_id: int
) -> list[sqlite3.Row]:
    return list(
        ligacao.execute(
            "SELECT * FROM mensagens WHERE conversa_id = ? ORDER BY id",
            (conversa_id,),
        ).fetchall()
    )


def meta_de(mensagem: sqlite3.Row) -> dict:
    bruto = mensagem["meta_json"]
    if not bruto:
        return {}
    return json.loads(bruto)
