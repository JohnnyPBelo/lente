"""Indexação mínima sem pesos: blocos + frases + FTS5 (caminho feliz .md/.txt).

Quando EmbeddingGemma não está em disco, a biblioteca continua utilizável:
o texto fica pesquisável por FTS e a procura devolve excertos literais.

Documentos grandes (Gutenberg) são cortados em blocos ~500 palavras — a unidade
de retrieval FTS — e as frases ficam na tabela ``frases`` para highlight, sem
duplicar cada frase no índice FTS (ADR-012).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from engine.embeddings.cortar import cortar_blocos, TokenizadorPalavras
from engine.embeddings.frases import segmentar_frases
from engine.embeddings.indexar import gerar_miniatura
from engine.pesquisa.fts import indexar_bloco


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def nome_ficheiro_miniatura(documento_id: int, pagina: int = 1) -> str:
    """Nome estável servido em ``/media/thumbs/…``."""
    return f"doc_{documento_id}_p{pagina}.png"


def url_miniatura(documento_id: int, pagina: int = 1) -> str:
    """URL HTTP da miniatura gerada na indexação."""
    return f"/media/thumbs/{nome_ficheiro_miniatura(documento_id, pagina)}"


def indexar_texto_fts(
    ligacao: sqlite3.Connection,
    *,
    documento_id: int,
    texto: str,
    hash_id: int | None = None,
    pasta_miniaturas: Path | str | None = None,
) -> int:
    """Grava blocos + frases e popula FTS (só blocos). Devolve o nº de frases."""
    corpo = (texto or "").strip()
    if not corpo:
        ligacao.execute(
            "UPDATE documentos SET estado = 'ok', actualizado_em = ?, indexado_em = ? "
            "WHERE id = ?",
            (_agora(), _agora(), documento_id),
        )
        ligacao.commit()
        return 0

    if hash_id is None:
        linha = ligacao.execute(
            "SELECT id FROM documento_hashes "
            "WHERE documento_id = ? AND activa = 1",
            (documento_id,),
        ).fetchone()
        if linha is None:
            raise LookupError(f"hash activa em falta para documento {documento_id}")
        hash_id = int(linha["id"] if hasattr(linha, "keys") else linha[0])

    # Limpa geração anterior deste hash (reindexação) — uma transacção.
    ligacao.execute(
        "DELETE FROM frases WHERE bloco_id IN "
        "(SELECT id FROM blocos WHERE hash_id = ?)",
        (hash_id,),
    )
    ligacao.execute("DELETE FROM blocos WHERE hash_id = ?", (hash_id,))
    ligacao.execute("DELETE FROM fts_texto WHERE hash_id = ?", (hash_id,))

    blocos = cortar_blocos(corpo, tokenizador=TokenizadorPalavras())
    if not blocos:
        # Texto sem «palavras» detectáveis — um bloco único.
        from engine.embeddings.cortar import BlocoCortado

        blocos = [
            BlocoCortado(
                texto=corpo,
                offset_inicio=0,
                offset_fim=len(corpo),
                tokens_aprox=max(1, len(corpo.split())),
                ordem=0,
            )
        ]

    total_frases = 0
    # Retrieval FTS = blocos (ADR-012). Frases ficam só na tabela ``frases``
    # para highlight; a procura refina o excerto a partir delas.
    frases_rows: list[tuple[int, int, int, str, int, int, int]] = []

    for bloco in blocos:
        cur = ligacao.execute(
            "INSERT INTO blocos ("
            "documento_id, hash_id, ordem, texto, "
            "pagina_inicio, pagina_fim, offset_inicio, offset_fim, tokens_aprox"
            ") VALUES (?, ?, ?, ?, 1, 1, ?, ?, ?)",
            (
                documento_id,
                hash_id,
                bloco.ordem,
                bloco.texto,
                bloco.offset_inicio,
                bloco.offset_fim,
                bloco.tokens_aprox,
            ),
        )
        bloco_id = int(cur.lastrowid)
        indexar_bloco(
            ligacao,
            bloco_id=bloco_id,
            texto=bloco.texto,
            documento_id=documento_id,
            hash_id=hash_id,
        )

        frases = segmentar_frases(bloco.texto, offset_base=bloco.offset_inicio)
        if not frases:
            frases_rows.append(
                (
                    bloco_id,
                    documento_id,
                    1,
                    bloco.texto,
                    bloco.offset_inicio,
                    bloco.offset_fim,
                    0,
                )
            )
            total_frases += 1
            continue

        for frase in frases:
            frases_rows.append(
                (
                    bloco_id,
                    documento_id,
                    frase.pagina or 1,
                    frase.texto,
                    frase.offset_inicio,
                    frase.offset_fim,
                    frase.ordem,
                )
            )
            total_frases += 1

    if frases_rows:
        ligacao.executemany(
            "INSERT INTO frases ("
            "bloco_id, documento_id, pagina, texto, "
            "offset_inicio, offset_fim, caixas_json, ordem"
            ") VALUES (?, ?, ?, ?, ?, ?, NULL, ?)",
            frases_rows,
        )

    momento = _agora()
    miniatura_caminho: str | None = None
    if pasta_miniaturas is not None:
        destino = Path(pasta_miniaturas) / nome_ficheiro_miniatura(documento_id, 1)
        gerado = gerar_miniatura(destino, texto=corpo[:200])
        miniatura_caminho = str(gerado)

    if miniatura_caminho is not None:
        ligacao.execute(
            "UPDATE documentos SET estado = 'ok', paginas = 1, "
            "miniatura_caminho = ?, actualizado_em = ?, indexado_em = ? "
            "WHERE id = ?",
            (miniatura_caminho, momento, momento, documento_id),
        )
    else:
        ligacao.execute(
            "UPDATE documentos SET estado = 'ok', paginas = 1, "
            "actualizado_em = ?, indexado_em = ? WHERE id = ?",
            (momento, momento, documento_id),
        )
    ligacao.commit()
    return total_frases
