"""Popular e consultar a tabela virtual FTS5 no mesmo ficheiro SQLite."""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class HitFts:
    """Candidato lexical antes do juiz (sem scores RRF)."""

    origem: str
    origem_id: int
    documento_id: int
    hash_id: int
    texto: str


_TOKEN = re.compile(r"[0-9A-Za-z_]+")


def _consulta_segura(termo: str) -> str:
    """Converte o termo em MATCH FTS5 sem interpretar hífens como NOT."""
    tokens = _TOKEN.findall(termo)
    if not tokens:
        return '""'
    return " AND ".join(f'"{t}"' for t in tokens)


def indexar_bloco(
    ligacao: sqlite3.Connection,
    *,
    bloco_id: int,
    texto: str,
    documento_id: int,
    hash_id: int,
) -> None:
    """Insere (ou substitui) o texto de um bloco no FTS5."""
    ligacao.execute(
        "DELETE FROM fts_texto WHERE origem = 'bloco' AND origem_id = ?",
        (bloco_id,),
    )
    ligacao.execute(
        "INSERT INTO fts_texto (texto, origem, origem_id, documento_id, hash_id) "
        "VALUES (?, 'bloco', ?, ?, ?)",
        (texto, bloco_id, documento_id, hash_id),
    )
    ligacao.commit()


def indexar_frase(
    ligacao: sqlite3.Connection,
    *,
    frase_id: int,
    texto: str,
    documento_id: int,
    hash_id: int,
) -> None:
    """Insere (ou substitui) o texto de uma frase no FTS5."""
    ligacao.execute(
        "DELETE FROM fts_texto WHERE origem = 'frase' AND origem_id = ?",
        (frase_id,),
    )
    ligacao.execute(
        "INSERT INTO fts_texto (texto, origem, origem_id, documento_id, hash_id) "
        "VALUES (?, 'frase', ?, ?, ?)",
        (texto, frase_id, documento_id, hash_id),
    )
    ligacao.commit()


def apagar_fts_hash(ligacao: sqlite3.Connection, hash_id: int) -> None:
    """Remove linhas FTS de uma geração (reindexação / delete)."""
    ligacao.execute("DELETE FROM fts_texto WHERE hash_id = ?", (hash_id,))
    ligacao.commit()


def procurar_fts(ligacao: sqlite3.Connection, termo: str, *, limite: int = 50) -> list[HitFts]:
    """Devolve hits FTS5 para o termo (identificadores literais incluídos)."""
    consulta = _consulta_segura(termo)
    linhas = ligacao.execute(
        "SELECT origem, origem_id, documento_id, hash_id, texto "
        "FROM fts_texto WHERE fts_texto MATCH ? LIMIT ?",
        (consulta, limite),
    ).fetchall()
    return [
        HitFts(
            origem=str(linha[0]),
            origem_id=int(linha[1]),
            documento_id=int(linha[2]),
            hash_id=int(linha[3]),
            texto=str(linha[4]),
        )
        for linha in linhas
    ]
