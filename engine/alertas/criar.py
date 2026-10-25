"""Criação, listagem e interruptor de alertas (máx. dez)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from engine.alertas.limite import MAX_ALERTAS, LimiteAlertas

PLACEHOLDER_VIGIA = "O que queres que eu vigie?"

_LENTES = frozenset({"investigar", "assessment", "acreditacao", "verificar"})


@dataclass(frozen=True)
class Alerta:
    """Alerta persistido com o seu fio."""

    id: int
    consulta: str
    lente: str | None
    activo: bool
    conversa_id: int


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _contar(ligacao: sqlite3.Connection) -> int:
    return int(ligacao.execute("SELECT COUNT(*) AS n FROM alertas").fetchone()["n"])


def criar_alerta(
    ligacao: sqlite3.Connection,
    consulta: str,
    *,
    lente: str | None = "investigar",
) -> Alerta:
    """Persiste um alerta e o fio associado. Levanta ``LimiteAlertas`` no 11.º."""
    texto = (consulta or "").strip()
    if not texto:
        raise ValueError("consulta de alerta vazia")
    if lente is not None and lente not in _LENTES:
        raise ValueError(f"lente inválida: {lente}")
    if _contar(ligacao) >= MAX_ALERTAS:
        raise LimiteAlertas()

    momento = _agora()
    titulo = texto if len(texto) <= 80 else texto[:77] + "…"
    cur_conv = ligacao.execute(
        "INSERT INTO conversas (titulo, criado_em, actualizado_em) "
        "VALUES (?, ?, ?)",
        (titulo, momento, momento),
    )
    conversa_id = int(cur_conv.lastrowid)
    cur = ligacao.execute(
        "INSERT INTO alertas ("
        "consulta, lente, activo, conversa_id, criado_em, actualizado_em"
        ") VALUES (?, ?, 1, ?, ?, ?)",
        (texto, lente, conversa_id, momento, momento),
    )
    return Alerta(
        id=int(cur.lastrowid),
        consulta=texto,
        lente=lente,
        activo=True,
        conversa_id=conversa_id,
    )


def listar_alertas(ligacao: sqlite3.Connection) -> list[Alerta]:
    """Lista todos os alertas (activos e desligados), por id."""
    linhas = ligacao.execute(
        "SELECT id, consulta, lente, activo, conversa_id FROM alertas ORDER BY id"
    ).fetchall()
    return [
        Alerta(
            id=int(l["id"]),
            consulta=l["consulta"],
            lente=l["lente"],
            activo=bool(l["activo"]),
            conversa_id=int(l["conversa_id"]),
        )
        for l in linhas
    ]


def definir_activo(
    ligacao: sqlite3.Connection,
    alerta_id: int,
    activo: bool,
) -> Alerta:
    """Interruptor no topo do fio: liga ou desliga emissões futuras."""
    momento = _agora()
    ligacao.execute(
        "UPDATE alertas SET activo = ?, actualizado_em = ? WHERE id = ?",
        (1 if activo else 0, momento, alerta_id),
    )
    linha = ligacao.execute(
        "SELECT id, consulta, lente, activo, conversa_id FROM alertas WHERE id = ?",
        (alerta_id,),
    ).fetchone()
    if linha is None:
        raise KeyError(f"alerta inexistente: {alerta_id}")
    return Alerta(
        id=int(linha["id"]),
        consulta=linha["consulta"],
        lente=linha["lente"],
        activo=bool(linha["activo"]),
        conversa_id=int(linha["conversa_id"]),
    )
