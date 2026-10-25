"""Avaliação de alertas só sobre frases de um documento acabado de indexar.

Sem E2B: o juiz pontua; se passar o limiar, cai mensagem no fio com miniatura.
Documentos antigos não são revistos sozinhos (``novo=False`` ou ``em_idle``).
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol, Sequence

from engine.alertas.prefixos import consulta_com_prefixo
from engine.juiz.pontuar import pontuar


class _SessaoAvaliavel(Protocol):
    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]: ...


@dataclass(frozen=True)
class MensagemAlerta:
    """Mensagem criada no fio de um alerta."""

    id: int
    alerta_id: int
    conversa_id: int
    documento_id: int


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _alertas_activos(ligacao: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(
        ligacao.execute(
            "SELECT id, consulta, lente, conversa_id FROM alertas "
            "WHERE activo = 1 ORDER BY id"
        ).fetchall()
    )


def _frases_do_documento(
    ligacao: sqlite3.Connection, documento_id: int
) -> list[sqlite3.Row]:
    return list(
        ligacao.execute(
            "SELECT id, texto FROM frases WHERE documento_id = ? ORDER BY ordem, id",
            (documento_id,),
        ).fetchall()
    )


def _miniatura(
    ligacao: sqlite3.Connection, documento_id: int
) -> str | None:
    linha = ligacao.execute(
        "SELECT miniatura_caminho FROM documentos WHERE id = ?",
        (documento_id,),
    ).fetchone()
    if linha is None:
        return None
    return linha["miniatura_caminho"]


def _gravar_mensagem(
    ligacao: sqlite3.Connection,
    *,
    alerta_id: int,
    conversa_id: int,
    documento_id: int,
    lente: str | None,
    excerto: str,
    miniatura_caminho: str | None,
    pontuacao: float,
) -> MensagemAlerta:
    momento = _agora()
    meta = {
        "documento_id": documento_id,
        "miniatura_caminho": miniatura_caminho,
        "pontuacao_juiz": pontuacao,
        "alerta_id": alerta_id,
    }
    cur = ligacao.execute(
        "INSERT INTO mensagens ("
        "conversa_id, papel, modo, lente, conteudo, meta_json, criado_em"
        ") VALUES (?, 'assistente', 'alerta', ?, ?, ?, ?)",
        (
            conversa_id,
            lente,
            excerto,
            json.dumps(meta, ensure_ascii=False),
            momento,
        ),
    )
    ligacao.execute(
        "UPDATE conversas SET actualizado_em = ? WHERE id = ?",
        (momento, conversa_id),
    )
    return MensagemAlerta(
        id=int(cur.lastrowid),
        alerta_id=alerta_id,
        conversa_id=conversa_id,
        documento_id=documento_id,
    )


def avaliar_documento_novo(
    ligacao: sqlite3.Connection,
    documento_id: int,
    *,
    sessao: _SessaoAvaliavel,
    limiar: float = 0.5,
    novo: bool = True,
    escritor: Any = None,
) -> list[MensagemAlerta]:
    """Avalia só as frases deste documento face aos alertas activos.

    Se ``novo`` for falso (reindexação de documento antigo na política), não dispara.
    ``escritor`` é ignorado de propósito — alertas não chamam o E2B.
    """
    del escritor  # contrato: sem prosa E2B nos alertas
    if not novo:
        return []

    frases_rows = _frases_do_documento(ligacao, documento_id)
    if not frases_rows:
        return []

    textos = [r["texto"] for r in frases_rows]
    miniatura = _miniatura(ligacao, documento_id)
    criadas: list[MensagemAlerta] = []

    for alerta in _alertas_activos(ligacao):
        pergunta = consulta_com_prefixo(alerta["consulta"], alerta["lente"])
        scores = pontuar(pergunta, textos, sessao=sessao)
        melhor_i = max(range(len(scores)), key=lambda i: scores[i])
        if scores[melhor_i] < limiar:
            continue
        criadas.append(
            _gravar_mensagem(
                ligacao,
                alerta_id=int(alerta["id"]),
                conversa_id=int(alerta["conversa_id"]),
                documento_id=documento_id,
                lente=alerta["lente"],
                excerto=textos[melhor_i],
                miniatura_caminho=miniatura,
                pontuacao=float(scores[melhor_i]),
            )
        )
    return criadas


def avaliar_apos_indexacao(
    ligacao: sqlite3.Connection,
    documento_id: int,
    *,
    sessao: _SessaoAvaliavel,
    limiar: float = 0.5,
    foi_novo: bool = True,
) -> list[MensagemAlerta]:
    """Gancho no fim da indexação (também após retoma de pausa por procura)."""
    return avaliar_documento_novo(
        ligacao,
        documento_id,
        sessao=sessao,
        limiar=limiar,
        novo=foi_novo,
    )


def em_idle(
    ligacao: sqlite3.Connection,
    *,
    sessao: _SessaoAvaliavel | None = None,
    limiar: float = 0.5,
) -> None:
    """Idle explícito: não relê a biblioteca nem emite mensagens.

    Existe para a política «documentos antigos não são revistos sozinhos»
    e para REG-FOR-002 — não há job de varrimento completo.
    """
    del ligacao, sessao, limiar
    return None
