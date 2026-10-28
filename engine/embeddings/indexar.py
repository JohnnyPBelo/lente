"""Orquestra documento → blocos / frases / vectores e miniatura."""

from __future__ import annotations

import sqlite3
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

from engine.embeddings.carregar import (
    DIMENSAO,
    SessaoEmbedding,
    embutir_lote,
)
from engine.embeddings.cortar import BlocoCortado, cortar_blocos
from engine.embeddings.frases import FraseSegmentada, segmentar_frases
from engine.embeddings.prefixos import prefixo_documento
from engine.ingestao.caixas import Caixa, caixas_para_json
from engine.pesquisa.fts import indexar_bloco


@dataclass(frozen=True)
class ResultadoIndexacao:
    """Resumo após indexar um documento na BD."""

    documento_id: int
    blocos: int
    frases: int
    miniatura_caminho: str | None


def guardar_vector(
    ligacao: sqlite3.Connection,
    bloco_id: int,
    vec: Sequence[float],
) -> None:
    """Persiste o vector 256d via ``engine.pesquisa.vec`` (mesmo SQLite / cosseno exacto)."""
    from engine.pesquisa.vec import guardar_vector as persistir_vector

    if len(vec) != DIMENSAO:
        raise ValueError(f"vector tem de ter {DIMENSAO} dimensões, não {len(vec)}")
    linha = ligacao.execute(
        "SELECT hash_id FROM blocos WHERE id = ?",
        (bloco_id,),
    ).fetchone()
    if linha is None:
        raise LookupError(f"bloco {bloco_id} inexistente para guardar vector")
    hash_id = int(linha[0] if not hasattr(linha, "keys") else linha["hash_id"])
    persistir_vector(
        ligacao,
        bloco_id=bloco_id,
        hash_id=hash_id,
        vector=vec,
    )


def gerar_miniatura(
    destino: Path | str,
    *,
    renderizar_pagina: Callable[[], bytes] | None = None,
    texto: str | None = None,
) -> Path:
    """Grava uma imagem pequena uma vez; ``renderizar_pagina`` só corre se preciso."""
    caminho = Path(destino)
    if caminho.is_file():
        return caminho
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if renderizar_pagina is not None:
        dados = renderizar_pagina()
    else:
        dados = construir_png_miniatura(texto=texto)
    caminho.write_bytes(dados)
    return caminho


def obter_miniatura_indexada(
    caminho: Path | str,
    *,
    renderizar_pdf: Callable[..., bytes] | None = None,
) -> bytes:
    """Lê a miniatura persistida; nunca re-renderiza o PDF no hover."""
    del renderizar_pdf
    return Path(caminho).read_bytes()


def indexar_documento(
    ligacao: sqlite3.Connection,
    *,
    documento_id: int,
    texto: str,
    titulo: str | None,
    sessao: SessaoEmbedding,
    tokenizador: Any,
    hash_id: int | None = None,
    caixas_por_intervalo: list[tuple[int, int, list[Caixa]]] | None = None,
    pasta_miniaturas: Path | str | None = None,
    pagina_visualizavel: bool = False,
    renderizar_pagina: Callable[[], bytes] | None = None,
) -> ResultadoIndexacao:
    """Corta, segmenta, embute e grava blocos/frases/vectores (+ miniatura)."""
    if hash_id is None:
        linha = ligacao.execute(
            "SELECT id FROM documento_hashes "
            "WHERE documento_id = ? AND activa = 1",
            (documento_id,),
        ).fetchone()
        if linha is None:
            raise LookupError(f"hash activa em falta para documento {documento_id}")
        hash_id = int(linha[0] if not hasattr(linha, "keys") else linha["id"])

    blocos = cortar_blocos(texto, tokenizador=tokenizador)
    total_frases = 0
    miniatura_caminho: str | None = None

    entradas = [prefixo_documento(titulo, b.texto) for b in blocos]
    vectores = embutir_lote(entradas, sessao=sessao) if entradas else []

    for bloco, vector in zip(blocos, vectores, strict=True):
        bloco_id = _inserir_bloco(
            ligacao,
            documento_id=documento_id,
            hash_id=hash_id,
            bloco=bloco,
        )
        guardar_vector(ligacao, bloco_id, vector)
        indexar_bloco(
            ligacao,
            bloco_id=bloco_id,
            texto=bloco.texto,
            documento_id=documento_id,
            hash_id=hash_id,
        )

        locais = _caixas_relativas_ao_bloco(bloco, caixas_por_intervalo or [])
        frases = segmentar_frases(
            bloco.texto,
            offset_base=bloco.offset_inicio,
            caixas_por_intervalo=locais,
        )
        for frase in frases:
            _inserir_frase(
                ligacao,
                documento_id=documento_id,
                bloco_id=bloco_id,
                frase=frase,
            )
            total_frases += 1

    if pagina_visualizavel and pasta_miniaturas is not None:
        destino = Path(pasta_miniaturas) / f"doc_{documento_id}_p1.png"
        gerado = gerar_miniatura(destino, renderizar_pagina=renderizar_pagina)
        miniatura_caminho = str(gerado)
        ligacao.execute(
            "UPDATE documentos SET miniatura_caminho = ? WHERE id = ?",
            (miniatura_caminho, documento_id),
        )

    ligacao.commit()
    return ResultadoIndexacao(
        documento_id=documento_id,
        blocos=len(blocos),
        frases=total_frases,
        miniatura_caminho=miniatura_caminho,
    )


def construir_png_miniatura(
    largura: int = 96,
    altura: int = 128,
    *,
    texto: str | None = None,
) -> bytes:
    """PNG legível sem Pillow: fundo claro, margem e linhas a sugerir texto.

    Issue #59 — o placeholder 32×32 cinza uniforme lia-se como «vazio».
    """

    def chunk(tipo: bytes, dados: bytes) -> bytes:
        return (
            struct.pack(">I", len(dados))
            + tipo
            + dados
            + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF)
        )

    fundo = (248, 248, 246)
    margem = (60, 60, 58)
    linha = (90, 90, 88)
    # Semáforo de conteúdo: variação estável a partir do texto.
    semente = sum(ord(c) for c in (texto or "lente")[:48]) % 40

    pixels: list[bytes] = []
    for y in range(altura):
        fila: list[int] = []
        for x in range(largura):
            borda = x < 2 or y < 2 or x >= largura - 2 or y >= altura - 2
            if borda:
                r, g, b = margem
            elif 12 <= y % 16 <= 14 and 8 <= x <= largura - 10:
                # Linhas horizontais tipo parágrafo.
                tom = max(40, linha[0] - (semente // 2))
                r = g = b = tom
            else:
                r = min(255, fundo[0] + (semente % 8))
                g = min(255, fundo[1] + ((semente + y) % 6))
                b = min(255, fundo[2] + ((semente + x) % 6))
            fila.extend((r, g, b))
        pixels.append(b"\x00" + bytes(fila))

    ihdr = struct.pack(">IIBBBBB", largura, altura, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(b"".join(pixels), 6))
        + chunk(b"IEND", b"")
    )


def _inserir_bloco(
    ligacao: sqlite3.Connection,
    *,
    documento_id: int,
    hash_id: int,
    bloco: BlocoCortado,
) -> int:
    cur = ligacao.execute(
        "INSERT INTO blocos ("
        "documento_id, hash_id, ordem, texto, "
        "pagina_inicio, pagina_fim, offset_inicio, offset_fim, tokens_aprox"
        ") VALUES (?, ?, ?, ?, NULL, NULL, ?, ?, ?)",
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
    return int(cur.lastrowid)


def _inserir_frase(
    ligacao: sqlite3.Connection,
    *,
    documento_id: int,
    bloco_id: int,
    frase: FraseSegmentada,
) -> int:
    cur = ligacao.execute(
        "INSERT INTO frases ("
        "bloco_id, documento_id, pagina, texto, "
        "offset_inicio, offset_fim, caixas_json, ordem"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            bloco_id,
            documento_id,
            frase.pagina,
            frase.texto,
            frase.offset_inicio,
            frase.offset_fim,
            caixas_para_json(frase.caixas),
            frase.ordem,
        ),
    )
    return int(cur.lastrowid)


def _caixas_relativas_ao_bloco(
    bloco: BlocoCortado,
    intervalos: list[tuple[int, int, list[Caixa]]],
) -> list[tuple[int, int, list[Caixa]]]:
    saida: list[tuple[int, int, list[Caixa]]] = []
    for i0, i1, caixas in intervalos:
        if i1 <= bloco.offset_inicio or i0 >= bloco.offset_fim:
            continue
        saida.append(
            (
                max(0, i0 - bloco.offset_inicio),
                min(len(bloco.texto), i1 - bloco.offset_inicio),
                caixas,
            )
        )
    return saida


__all__ = [
    "ResultadoIndexacao",
    "construir_png_miniatura",
    "gerar_miniatura",
    "guardar_vector",
    "indexar_documento",
    "obter_miniatura_indexada",
]
