"""Motor de procura: FTS local; degrada a vazio sem índice."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Callable

from engine.api.ids import doc_id
from engine.armazenamento.repositorio import abrir
from engine.ingestao.indexar_minimo import url_miniatura
from engine.pesquisa.fts import procurar_fts

MotorProcura = Callable[..., dict[str, Any]]


def motor_procura_sem_e2b(
    *,
    chat_id: str,
    texto: str,
    lente: str,
    pagina_aberta: dict[str, Any] | None = None,
    com_e2b: bool = False,
    **_kwargs: Any,
) -> dict[str, Any]:
    """Sem BD ligada: devolve vazio (a API emite evento ``vazio``)."""
    del chat_id, texto, lente, pagina_aberta, com_e2b
    return {"excertos": [], "frases": [], "miniaturas": []}


def _offsets_e_pagina(
    ligacao: sqlite3.Connection, hit: Any
) -> tuple[dict[str, int], int]:
    if hit.origem == "frase":
        linha = ligacao.execute(
            "SELECT pagina, offset_inicio, offset_fim FROM frases WHERE id = ?",
            (hit.origem_id,),
        ).fetchone()
        if linha is not None:
            return (
                {
                    "inicio": int(linha["offset_inicio"]),
                    "fim": int(linha["offset_fim"]),
                },
                int(linha["pagina"] or 1),
            )
    elif hit.origem == "bloco":
        linha = ligacao.execute(
            "SELECT offset_inicio, offset_fim FROM blocos WHERE id = ?",
            (hit.origem_id,),
        ).fetchone()
        if linha is not None:
            return (
                {
                    "inicio": int(linha["offset_inicio"]),
                    "fim": int(linha["offset_fim"]),
                },
                1,
            )
    return {"inicio": 0, "fim": len(hit.texto or "")}, 1


def _url_miniatura_doc(
    ligacao: sqlite3.Connection, documento_numero: int, pagina: int
) -> str:
    linha = ligacao.execute(
        "SELECT miniatura_caminho FROM documentos WHERE id = ?",
        (documento_numero,),
    ).fetchone()
    if linha is not None and linha["miniatura_caminho"]:
        nome = Path(str(linha["miniatura_caminho"])).name
        if nome:
            return f"/media/thumbs/{nome}"
    return url_miniatura(documento_numero, pagina)


def motor_procura_fts(caminho_sqlite: Path | str) -> MotorProcura:
    """Procura lexical no mesmo SQLite; sem embeddings/juiz (modelos ausentes)."""

    caminho = Path(caminho_sqlite)

    def _motor(
        *,
        chat_id: str,
        texto: str,
        lente: str,
        pagina_aberta: dict[str, Any] | None = None,
        com_e2b: bool = False,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        del chat_id, lente, pagina_aberta, com_e2b
        ligacao = abrir(caminho)
        # Preferir frases; evitar duplicar o mesmo texto bloco+frase.
        hits = procurar_fts(ligacao, texto.strip(), limite=40)
        hits = sorted(hits, key=lambda h: 0 if h.origem == "frase" else 1)
        excertos: list[dict[str, Any]] = []
        miniaturas: list[dict[str, Any]] = []
        vistos_doc: set[str] = set()
        vistos_texto: set[str] = set()
        for hit in hits:
            chave = (hit.texto or "").strip()
            if chave in vistos_texto:
                continue
            vistos_texto.add(chave)
            offsets, pagina = _offsets_e_pagina(ligacao, hit)
            numero = int(hit.documento_id)
            documento = doc_id(numero)
            excertos.append(
                {
                    "n": len(excertos) + 1,
                    "documento_id": documento,
                    "pagina": pagina,
                    "texto": hit.texto,
                    "offsets": offsets,
                    "caixas": [],
                    "score_juiz": 1.0,
                }
            )
            if documento not in vistos_doc:
                vistos_doc.add(documento)
                miniaturas.append(
                    {
                        "documento_id": documento,
                        "pagina": pagina,
                        "url": _url_miniatura_doc(ligacao, numero, pagina),
                    }
                )
            if len(excertos) >= 20:
                break
        return {
            "excertos": excertos,
            "frases": [],
            "miniaturas": miniaturas,
        }

    return _motor
