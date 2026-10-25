"""Registo na biblioteca: ``documentos``, ``documento_hashes`` e fila."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from engine.ingestao import extrair
from engine.ingestao.hash import sha256_ficheiro
from engine.ingestao.tipos import FicheiroInexistente


@dataclass(frozen=True)
class DocumentoRegisto:
    """Identidade mínima devolvida após upsert."""

    id: int
    caminho: str
    sha256: str
    estado: str


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _titulo_de_caminho(caminho: Path) -> str:
    return caminho.stem or caminho.name


def _enfileirar(ligacao: sqlite3.Connection, documento_id: int, momento: str) -> None:
    """Garante no máximo uma linha ``pendente`` por documento."""
    existente = ligacao.execute(
        "SELECT id FROM fila WHERE documento_id = ? AND estado = 'pendente'",
        (documento_id,),
    ).fetchone()
    if existente is not None:
        return
    ligacao.execute(
        "INSERT INTO fila (documento_id, estado, prioridade, criado_em) "
        "VALUES (?, 'pendente', 100, ?)",
        (documento_id, momento),
    )


def _gravar_hash_activa(
    ligacao: sqlite3.Connection,
    documento_id: int,
    digest: str,
    momento: str,
) -> None:
    ligacao.execute(
        "UPDATE documento_hashes SET activa = 0 "
        "WHERE documento_id = ? AND activa = 1",
        (documento_id,),
    )
    anterior = ligacao.execute(
        "SELECT id FROM documento_hashes "
        "WHERE documento_id = ? AND sha256 = ?",
        (documento_id, digest),
    ).fetchone()
    if anterior is None:
        ligacao.execute(
            "INSERT INTO documento_hashes "
            "(documento_id, sha256, visto_em, activa) VALUES (?, ?, ?, 1)",
            (documento_id, digest, momento),
        )
    else:
        ligacao.execute(
            "UPDATE documento_hashes SET activa = 1, visto_em = ? WHERE id = ?",
            (momento, anterior["id"]),
        )


def registar_ficheiro(
    ligacao: sqlite3.Connection,
    caminho: Path | str,
) -> DocumentoRegisto:
    """Extrai, faz upsert em ``documentos`` + hashes e enfileira (``a_indexar``)."""
    destino = Path(caminho).resolve()
    if not destino.is_file():
        raise FicheiroInexistente(str(destino))

    extraccao = extrair(destino)
    digest = sha256_ficheiro(destino)
    momento = _agora()
    sumario = (
        json.dumps(extraccao.titulos, ensure_ascii=False)
        if extraccao.titulos
        else None
    )
    caminho_txt = str(destino)

    existente = ligacao.execute(
        "SELECT id, sha256 FROM documentos WHERE caminho = ?",
        (caminho_txt,),
    ).fetchone()

    if existente is None:
        cursor = ligacao.execute(
            "INSERT INTO documentos ("
            "caminho, titulo, tipo, sha256, estado, sumario_json, "
            "criado_em, actualizado_em"
            ") VALUES (?, ?, ?, ?, 'a_indexar', ?, ?, ?)",
            (
                caminho_txt,
                _titulo_de_caminho(destino),
                extraccao.tipo,
                digest,
                sumario,
                momento,
                momento,
            ),
        )
        documento_id = int(cursor.lastrowid)
    else:
        documento_id = int(existente["id"])
        ligacao.execute(
            "UPDATE documentos SET titulo = ?, tipo = ?, sha256 = ?, "
            "estado = 'a_indexar', sumario_json = ?, actualizado_em = ? "
            "WHERE id = ?",
            (
                _titulo_de_caminho(destino),
                extraccao.tipo,
                digest,
                sumario,
                momento,
                documento_id,
            ),
        )

    _gravar_hash_activa(ligacao, documento_id, digest, momento)
    _enfileirar(ligacao, documento_id, momento)
    ligacao.commit()
    return DocumentoRegisto(
        id=documento_id,
        caminho=caminho_txt,
        sha256=digest,
        estado="a_indexar",
    )


def registar_texto(
    ligacao: sqlite3.Connection,
    texto: str,
    caminho: Path | str,
) -> DocumentoRegisto:
    """Persiste texto colado em ``caminho`` e regista-o como ``.txt``."""
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    return registar_ficheiro(ligacao, destino)


def verificar_actualidade(
    ligacao: sqlite3.Connection,
    documento_id: int,
) -> str:
    """Compara o SHA em disco com o gravado; diverge → ``desactualizado``.

    Não reindexa sozinho: o índice antigo deixa de se tratar como actual.
    """
    linha = ligacao.execute(
        "SELECT caminho, sha256, estado FROM documentos WHERE id = ?",
        (documento_id,),
    ).fetchone()
    if linha is None:
        raise LookupError(f"Documento inexistente: {documento_id}")

    destino = Path(linha["caminho"])
    if not destino.is_file():
        momento = _agora()
        ligacao.execute(
            "UPDATE documentos SET estado = 'desactualizado', actualizado_em = ? "
            "WHERE id = ?",
            (momento, documento_id),
        )
        ligacao.commit()
        return "desactualizado"

    digest_disco = sha256_ficheiro(destino)
    if digest_disco == linha["sha256"]:
        return str(linha["estado"])

    momento = _agora()
    ligacao.execute(
        "UPDATE documentos SET estado = 'desactualizado', actualizado_em = ? "
        "WHERE id = ?",
        (momento, documento_id),
    )
    ligacao.commit()
    return "desactualizado"
