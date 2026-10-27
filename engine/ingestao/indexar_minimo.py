"""Indexação mínima sem pesos: blocos + frases + FTS5 (caminho feliz .md/.txt).

Quando EmbeddingGemma não está em disco, a biblioteca continua utilizável:
o texto fica pesquisável por FTS e a procura devolve excertos literais.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from engine.embeddings.frases import segmentar_frases
from engine.embeddings.indexar import gerar_miniatura
from engine.pesquisa.fts import indexar_bloco, indexar_frase


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
    """Grava um bloco + frases e popula FTS. Devolve o número de frases."""
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

    # Limpa geração anterior deste hash (reindexação)
    ligacao.execute(
        "DELETE FROM frases WHERE bloco_id IN "
        "(SELECT id FROM blocos WHERE hash_id = ?)",
        (hash_id,),
    )
    ligacao.execute("DELETE FROM blocos WHERE hash_id = ?", (hash_id,))
    ligacao.execute("DELETE FROM fts_texto WHERE hash_id = ?", (hash_id,))

    cur = ligacao.execute(
        "INSERT INTO blocos ("
        "documento_id, hash_id, ordem, texto, "
        "pagina_inicio, pagina_fim, offset_inicio, offset_fim, tokens_aprox"
        ") VALUES (?, ?, 0, ?, 1, 1, 0, ?, ?)",
        (
            documento_id,
            hash_id,
            corpo,
            len(corpo),
            max(1, len(corpo.split())),
        ),
    )
    bloco_id = int(cur.lastrowid)
    indexar_bloco(
        ligacao,
        bloco_id=bloco_id,
        texto=corpo,
        documento_id=documento_id,
        hash_id=hash_id,
    )

    frases = segmentar_frases(corpo, offset_base=0)
    if not frases:
        # Um único «bloco» como frase se a segmentação não partir nada
        cur_f = ligacao.execute(
            "INSERT INTO frases ("
            "bloco_id, documento_id, pagina, texto, "
            "offset_inicio, offset_fim, caixas_json, ordem"
            ") VALUES (?, ?, 1, ?, 0, ?, NULL, 0)",
            (bloco_id, documento_id, corpo, len(corpo)),
        )
        frase_id = int(cur_f.lastrowid)
        indexar_frase(
            ligacao,
            frase_id=frase_id,
            texto=corpo,
            documento_id=documento_id,
            hash_id=hash_id,
        )
        total = 1
    else:
        total = 0
        for frase in frases:
            cur_f = ligacao.execute(
                "INSERT INTO frases ("
                "bloco_id, documento_id, pagina, texto, "
                "offset_inicio, offset_fim, caixas_json, ordem"
                ") VALUES (?, ?, ?, ?, ?, ?, NULL, ?)",
                (
                    bloco_id,
                    documento_id,
                    frase.pagina or 1,
                    frase.texto,
                    frase.offset_inicio,
                    frase.offset_fim,
                    frase.ordem,
                ),
            )
            frase_id = int(cur_f.lastrowid)
            indexar_frase(
                ligacao,
                frase_id=frase_id,
                texto=frase.texto,
                documento_id=documento_id,
                hash_id=hash_id,
            )
            total += 1

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
    return total
