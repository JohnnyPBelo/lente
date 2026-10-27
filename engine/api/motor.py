"""Motor de procura: FTS degradado ou pipeline RRF+juiz(+E2B) com pesos."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Callable

from engine.api.ids import doc_id
from engine.armazenamento.repositorio import abrir
from engine.ingestao.indexar_minimo import url_miniatura
from engine.pesquisa.fts import HitFts, procurar_fts
from engine.runtime.pesos import estado_modelos

MotorProcura = Callable[..., dict[str, Any]]

_log = logging.getLogger(__name__)


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


def _offsets_por_chave(
    ligacao: sqlite3.Connection, chave: str, texto: str
) -> tuple[dict[str, int], int, int | None]:
    """Devolve offsets, página e documento_id numérico a partir de ``frase:N``/``bloco:N``."""
    if ":" not in chave:
        return {"inicio": 0, "fim": len(texto)}, 1, None
    origem, resto = chave.split(":", 1)
    try:
        origem_id = int(resto)
    except ValueError:
        return {"inicio": 0, "fim": len(texto)}, 1, None
    hit = type("H", (), {"origem": origem, "origem_id": origem_id, "texto": texto})()
    offsets, pagina = _offsets_e_pagina(ligacao, hit)
    documento_id: int | None = None
    if origem == "frase":
        linha = ligacao.execute(
            "SELECT b.documento_id FROM frases f "
            "JOIN blocos b ON b.id = f.bloco_id WHERE f.id = ?",
            (origem_id,),
        ).fetchone()
        if linha is not None:
            documento_id = int(linha["documento_id"])
    elif origem == "bloco":
        linha = ligacao.execute(
            "SELECT documento_id FROM blocos WHERE id = ?",
            (origem_id,),
        ).fetchone()
        if linha is not None:
            documento_id = int(linha["documento_id"])
    return offsets, pagina, documento_id


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
            "motor": "fts",
        }

    _motor.modo = "fts"  # type: ignore[attr-defined]
    return _motor


def _chave_hit(hit: HitFts) -> str:
    return f"{hit.origem}:{hit.origem_id}"


def motor_procura_pipeline(
    caminho_sqlite: Path | str,
    *,
    raiz_modelos: Path | str,
    com_embedding: bool = True,
) -> MotorProcura:
    """FTS (+ cosseno) → RRF → juiz → limiar; E2B opcional via ``com_e2b``."""

    caminho = Path(caminho_sqlite)
    raiz = Path(raiz_modelos)
    cache: dict[str, Any] = {"emb": None, "juiz": None, "falha_emb": False}

    def _sessao_juiz() -> Any:
        if cache["juiz"] is None:
            from engine.juiz.carregar import carregar_sessao

            cache["juiz"] = carregar_sessao(raiz_modelos=raiz)
        return cache["juiz"]

    def _sessao_emb() -> Any | None:
        if not com_embedding or cache["falha_emb"]:
            return None
        if cache["emb"] is None:
            try:
                from engine.embeddings.carregar import carregar_modelo

                cache["emb"] = carregar_modelo(raiz_modelos=raiz, dispositivo="cpu")
            except Exception as exc:  # noqa: BLE001 — degrada a FTS+juiz
                _log.warning("Embedding indisponível; RRF só com FTS: %s", exc)
                cache["falha_emb"] = True
                return None
        return cache["emb"]

    def _motor(
        *,
        chat_id: str,
        texto: str,
        lente: str,
        pagina_aberta: dict[str, Any] | None = None,
        com_e2b: bool = False,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        del chat_id
        pergunta = texto.strip()
        ligacao = abrir(caminho)

        try:
            return _correr_pipeline(
                ligacao,
                pergunta=pergunta,
                lente=lente,
                pagina_aberta=pagina_aberta,
                com_e2b=com_e2b,
                sessao_juiz=_sessao_juiz(),
                sessao_emb=_sessao_emb(),
                raiz_modelos=raiz,
            )
        except Exception as exc:  # noqa: BLE001 — nunca 500 por ML
            _log.exception("Pipeline ML falhou; degrada a FTS: %s", exc)
            return motor_procura_fts(caminho)(
                chat_id="",
                texto=pergunta,
                lente=lente,
                pagina_aberta=pagina_aberta,
                com_e2b=False,
            )

    _motor.modo = "pipeline"  # type: ignore[attr-defined]
    return _motor


def _correr_pipeline(
    ligacao: sqlite3.Connection,
    *,
    pergunta: str,
    lente: str,
    pagina_aberta: dict[str, Any] | None,
    com_e2b: bool,
    sessao_juiz: Any,
    sessao_emb: Any | None,
    raiz_modelos: Path,
) -> dict[str, Any]:
    from engine.embeddings.carregar import embutir
    from engine.embeddings.prefixos import prefixo_query
    from engine.pesquisa import pipeline as pl
    from engine.pesquisa.vec import procurar_cosseno

    hits_fts = procurar_fts(ligacao, pergunta, limite=40)
    ranking_fts = [_chave_hit(h) for h in hits_fts]
    textos: dict[str, str] = {_chave_hit(h): h.texto for h in hits_fts}
    cossenos: dict[str, float] = {}
    ranking_embedding: list[str] = []

    if sessao_emb is not None:
        try:
            n_vectores = ligacao.execute("SELECT COUNT(*) FROM vectores").fetchone()[0]
        except sqlite3.Error:
            n_vectores = 0
        if int(n_vectores) > 0:
            consulta = prefixo_query(pergunta, lente=lente)
            vector = embutir(consulta, sessao=sessao_emb)
            for viz in procurar_cosseno(ligacao, vector, limite=40):
                chave = f"bloco:{viz.bloco_id}"
                ranking_embedding.append(chave)
                cossenos[chave] = float(viz.cosseno)
                if chave not in textos:
                    linha = ligacao.execute(
                        "SELECT texto FROM blocos WHERE id = ?",
                        (viz.bloco_id,),
                    ).fetchone()
                    if linha is not None:
                        textos[chave] = str(linha["texto"])

    # Sem candidatos embedding: RRF ainda funde FTS consigo (lista vazia ok).
    highlights = pl.procurar(
        pergunta,
        ranking_fts=ranking_fts,
        ranking_embedding=ranking_embedding,
        textos=textos,
        sessao_juiz=sessao_juiz,
        cossenos=cossenos,
        lente=lente,
    )

    excertos: list[dict[str, Any]] = []
    miniaturas: list[dict[str, Any]] = []
    vistos_doc: set[str] = set()
    for hl in highlights:
        offsets, pagina, doc_num = _offsets_por_chave(ligacao, hl.id, hl.texto)
        if doc_num is None:
            continue
        documento = doc_id(doc_num)
        excertos.append(
            {
                "n": len(excertos) + 1,
                "documento_id": documento,
                "pagina": pagina,
                "texto": hl.texto,
                "offsets": offsets,
                "caixas": [],
                "score_juiz": float(hl.score),
            }
        )
        if documento not in vistos_doc:
            vistos_doc.add(documento)
            miniaturas.append(
                {
                    "documento_id": documento,
                    "pagina": pagina,
                    "url": _url_miniatura_doc(ligacao, doc_num, pagina),
                }
            )
        if len(excertos) >= 20:
            break

    frases: list[dict[str, Any]] = []
    if com_e2b and excertos:
        frases = _frases_e2b(
            pergunta=pergunta,
            lente=lente,
            excertos=excertos,
            pagina_aberta=pagina_aberta,
            sessao_juiz=sessao_juiz,
            raiz_modelos=raiz_modelos,
        )

    return {
        "excertos": excertos,
        "frases": frases,
        "miniaturas": miniaturas,
        "motor": "pipeline",
    }


def _frases_e2b(
    *,
    pergunta: str,
    lente: str,
    excertos: list[dict[str, Any]],
    pagina_aberta: dict[str, Any] | None,
    sessao_juiz: Any,
    raiz_modelos: Path | str | None,
) -> list[dict[str, Any]]:
    """Visita E2B; lista vazia se pesos/RAM falharem (excertos já vão na resposta)."""
    try:
        from engine.resposta.e2b import EscritorE2B
        from engine.resposta.gerar import gerar_resposta
        from engine.resposta.tipos import (
            Excerto,
            Miniatura,
            PaginaAberta,
            TrechoPacote,
        )

        escritor = EscritorE2B(raiz_modelos=raiz_modelos)
        if not escritor.disponivel():
            return []

        trechos = [
            TrechoPacote(
                n=int(ex["n"]),
                ficheiro=str(ex["documento_id"]),
                pagina=ex.get("pagina"),
                texto=str(ex["texto"]),
                documento_id=str(ex["documento_id"]),
                offset_inicio=(ex.get("offsets") or {}).get("inicio"),
                offset_fim=(ex.get("offsets") or {}).get("fim"),
            )
            for ex in excertos
        ]
        pag = None
        if isinstance(pagina_aberta, dict) and pagina_aberta.get("documento_id"):
            pag = PaginaAberta(
                documento_id=str(pagina_aberta["documento_id"]),
                pagina=int(pagina_aberta.get("pagina") or 1),
                texto=str(pagina_aberta.get("texto") or ""),
                ficheiro=pagina_aberta.get("ficheiro"),
            )
        resultado = gerar_resposta(
            pergunta=pergunta,
            trechos=trechos,
            modo="procurar",
            escritor=escritor,
            excertos=[
                Excerto(
                    n=int(ex["n"]),
                    documento_id=str(ex["documento_id"]),
                    pagina=ex.get("pagina"),
                    texto=str(ex["texto"]),
                    offset_inicio=(ex.get("offsets") or {}).get("inicio"),
                    offset_fim=(ex.get("offsets") or {}).get("fim"),
                )
                for ex in excertos
            ],
            miniaturas=[
                Miniatura(documento_id=str(ex["documento_id"]), pagina=ex.get("pagina"))
                for ex in excertos
            ],
            sessao_juiz=sessao_juiz,
            lente=lente,
            pagina_aberta=pag,
        )
        return [
            {
                "texto": f.texto,
                "citacoes": [{"n": f.n, "documento_id": trechos[f.n - 1].documento_id}]
                if 1 <= f.n <= len(trechos)
                else [],
            }
            for f in resultado.frases
        ]
    except Exception as exc:  # noqa: BLE001
        _log.warning("E2B visit falhou; seguem só excertos: %s", exc)
        return []


def pesos_permitem_pipeline(raiz_modelos: Path | str | None) -> bool:
    """Juiz residente é o mínimo para sair do stub FTS com score falso."""
    if raiz_modelos is None:
        return False
    estado = estado_modelos(raiz_modelos)
    return estado.get("juiz", {}).get("estado") == "pronto"


def embedding_pronto(raiz_modelos: Path | str | None) -> bool:
    if raiz_modelos is None:
        return False
    return estado_modelos(raiz_modelos).get("embedding", {}).get("estado") == "pronto"


def escritor_pronto(raiz_modelos: Path | str | None) -> bool:
    if raiz_modelos is None:
        return False
    return estado_modelos(raiz_modelos).get("escritor", {}).get("estado") == "pronto"


def selecionar_motor_procura(
    caminho_sqlite: Path | str | None,
    *,
    raiz_modelos: Path | str | None = None,
) -> MotorProcura:
    """Com juiz em disco → pipeline; senão FTS degradado; sem BD → vazio."""
    if caminho_sqlite is None:
        return motor_procura_sem_e2b
    if pesos_permitem_pipeline(raiz_modelos):
        return motor_procura_pipeline(
            caminho_sqlite,
            raiz_modelos=raiz_modelos or "models",
            com_embedding=embedding_pronto(raiz_modelos),
        )
    return motor_procura_fts(caminho_sqlite)


__all__ = [
    "MotorProcura",
    "embedding_pronto",
    "escritor_pronto",
    "motor_procura_fts",
    "motor_procura_pipeline",
    "motor_procura_sem_e2b",
    "pesos_permitem_pipeline",
    "selecionar_motor_procura",
]
