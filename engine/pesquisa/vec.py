"""Vectores 256-d no mesmo SQLite: cosseno exacto (sem índice aproximado).

Carrega ``sqlite-vec`` quando o pacote está instalado; se faltar, o varrimento
exacto sobre a tabela ``vectores`` (BLOB float32) continua a funcionar — a
regressão de cosseno exacto não depende da roda pip.
"""

from __future__ import annotations

import math
import sqlite3
import struct
from dataclasses import dataclass
from typing import Sequence

DIMENSOES = 256
_FMT = f"<{DIMENSOES}f"


@dataclass(frozen=True)
class ResultadoCosseno:
    """Vizinho por cosseno exacto (similaridade; 1.0 = idêntico se normalizado)."""

    bloco_id: int
    cosseno: float
    hash_id: int


def tipo_indice() -> str:
    """Sempre cosseno exacto — nunca ANN / Vec1."""
    return "exacto"


def carregar_extensao(ligacao: sqlite3.Connection) -> bool:
    """Tenta carregar sqlite-vec na ligação. Devolve True se ficou activa."""
    try:
        import sqlite_vec
    except ImportError:
        return False
    try:
        ligacao.enable_load_extension(True)
        try:
            sqlite_vec.load(ligacao)
        finally:
            ligacao.enable_load_extension(False)
        # Confirma que a API scalar existe (cosseno exacto, não ANN).
        ligacao.execute("SELECT vec_version()").fetchone()
        return True
    except (AttributeError, sqlite3.Error, OSError):
        return False


def normalizar(vector: Sequence[float]) -> list[float]:
    """L2-normaliza para cosseno = produto interno; exige ``DIMENSOES`` elementos."""
    if len(vector) != DIMENSOES:
        raise ValueError(f"Esperava {DIMENSOES} dimensões, recebeu {len(vector)}")
    norma = math.sqrt(sum(float(x) * float(x) for x in vector))
    if norma == 0.0:
        raise ValueError("Vector nulo não pode ser normalizado")
    return [float(x) / norma for x in vector]


def _serializar(vector: Sequence[float]) -> bytes:
    if len(vector) != DIMENSOES:
        raise ValueError(f"Esperava {DIMENSOES} dimensões, recebeu {len(vector)}")
    return struct.pack(_FMT, *[float(x) for x in vector])


def _deserializar(blob: bytes) -> list[float]:
    if len(blob) != DIMENSOES * 4:
        raise ValueError(f"BLOB com {len(blob)} bytes; esperado {DIMENSOES * 4}")
    return list(struct.unpack(_FMT, blob))


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(x) * float(y) for x, y in zip(a, b, strict=True))


def guardar_vector(
    ligacao: sqlite3.Connection,
    *,
    bloco_id: int,
    hash_id: int,
    vector: Sequence[float],
) -> None:
    """Persiste o embedding normalizado do bloco (substitui se já existir)."""
    carregar_extensao(ligacao)
    blob = _serializar(vector if _ja_normalizado(vector) else normalizar(vector))
    ligacao.execute(
        "INSERT INTO vectores (bloco_id, hash_id, dimensoes, embedding) "
        "VALUES (?, ?, ?, ?) "
        "ON CONFLICT(bloco_id) DO UPDATE SET "
        "hash_id = excluded.hash_id, "
        "dimensoes = excluded.dimensoes, "
        "embedding = excluded.embedding",
        (bloco_id, hash_id, DIMENSOES, blob),
    )
    ligacao.commit()


def _ja_normalizado(vector: Sequence[float], *, tol: float = 1e-3) -> bool:
    norma = math.sqrt(sum(float(x) * float(x) for x in vector))
    return abs(norma - 1.0) <= tol


def apagar_vectores_hash(ligacao: sqlite3.Connection, hash_id: int) -> None:
    """Remove vectores de uma geração (reindexação)."""
    ligacao.execute("DELETE FROM vectores WHERE hash_id = ?", (hash_id,))
    ligacao.commit()


def procurar_cosseno(
    ligacao: sqlite3.Connection,
    consulta: Sequence[float],
    *,
    limite: int = 50,
) -> list[ResultadoCosseno]:
    """Varrimento exacto: ordena todos os vectores por similaridade de cosseno.

    Com ``sqlite-vec`` disponível usa ``vec_distance_cosine`` (exacto).
    Sem a extensão, calcula o produto interno em Python sobre os BLOBs.
    Nunca activa ANN / Vec1.
    """
    if tipo_indice() != "exacto":
        raise RuntimeError("Índice aproximado recusado; só cosseno exacto")

    query = list(consulta if _ja_normalizado(consulta) else normalizar(consulta))
    tem_ext = carregar_extensao(ligacao)

    if tem_ext:
        return _procurar_via_sqlite_vec(ligacao, query, limite=limite)
    return _procurar_via_python(ligacao, query, limite=limite)


def _procurar_via_sqlite_vec(
    ligacao: sqlite3.Connection,
    query: Sequence[float],
    *,
    limite: int,
) -> list[ResultadoCosseno]:
    """Cosseno exacto com a função scalar da extensão (distância = 1 - cosseno)."""
    blob = _serializar(query)
    linhas = ligacao.execute(
        "SELECT bloco_id, hash_id, "
        "1.0 - vec_distance_cosine(embedding, ?) AS cosseno "
        "FROM vectores "
        "ORDER BY cosseno DESC "
        "LIMIT ?",
        (blob, limite),
    ).fetchall()
    return [
        ResultadoCosseno(
            bloco_id=int(linha[0]),
            hash_id=int(linha[1]),
            cosseno=float(linha[2]),
        )
        for linha in linhas
    ]


def _procurar_via_python(
    ligacao: sqlite3.Connection,
    query: Sequence[float],
    *,
    limite: int,
) -> list[ResultadoCosseno]:
    """Double / caminho sem roda: varrimento exacto em processo sobre o mesmo ficheiro."""
    linhas = ligacao.execute(
        "SELECT bloco_id, hash_id, embedding FROM vectores"
    ).fetchall()
    pontuados: list[ResultadoCosseno] = []
    for bloco_id, hash_id, blob in linhas:
        vec = _deserializar(bytes(blob))
        pontuados.append(
            ResultadoCosseno(
                bloco_id=int(bloco_id),
                hash_id=int(hash_id),
                cosseno=_dot(query, vec),
            )
        )
    pontuados.sort(key=lambda r: r.cosseno, reverse=True)
    return pontuados[:limite]
