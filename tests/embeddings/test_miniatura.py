"""Regressão REG-ING-011: miniatura na indexação; pesos ausentes com caminho."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from engine.armazenamento.repositorio import abrir
from engine.embeddings.carregar import PesosEmbeddingAusentes, carregar_modelo, caminho_pesos
from engine.embeddings.indexar import (
    indexar_documento,
    obter_miniatura_indexada,
)
from tests.embeddings import apoio
from tests.embeddings.test_cortar import TokenizadorPalavras


def _agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def test_reg_ing_011(caminho_tmp: Path, tmp_path: Path) -> None:
    """Miniatura persistida sem re-render; HF em falta → caminho local, sem download."""
    ligacao = abrir(caminho_tmp)
    momento = _agora()
    ligacao.execute(
        "INSERT INTO documentos ("
        "caminho, titulo, tipo, sha256, estado, criado_em, actualizado_em"
        ") VALUES (?, ?, 'pdf', ?, 'a_indexar', ?, ?)",
        (str(tmp_path / "doc.pdf"), "Doc sintetico", "abc" * 10 + "def0", momento, momento),
    )
    doc_id = int(ligacao.execute("SELECT last_insert_rowid()").fetchone()[0])
    ligacao.execute(
        "INSERT INTO documento_hashes (documento_id, sha256, visto_em, activa) "
        "VALUES (?, ?, ?, 1)",
        (doc_id, "abc" * 10 + "def0", momento),
    )
    ligacao.commit()

    pasta_thumbs = tmp_path / "miniaturas"
    render_chamadas: list[int] = []

    def renderizar_uma_vez() -> bytes:
        render_chamadas.append(1)
        return b"\x89PNG\r\n\x1a\nminiatura-sintetica"

    resultado = indexar_documento(
        ligacao,
        documento_id=doc_id,
        texto="Frase sintetica curta para indexar a miniatura.",
        titulo="Doc sintetico",
        sessao=apoio.sessao_dupla(),
        tokenizador=TokenizadorPalavras(),
        pasta_miniaturas=pasta_thumbs,
        pagina_visualizavel=True,
        renderizar_pagina=renderizar_uma_vez,
    )
    assert resultado.miniatura_caminho is not None
    caminho_mini = Path(resultado.miniatura_caminho)
    assert caminho_mini.is_file()
    assert len(render_chamadas) == 1

    linha = ligacao.execute(
        "SELECT miniatura_caminho FROM documentos WHERE id = ?",
        (doc_id,),
    ).fetchone()
    assert linha[0] == str(caminho_mini)

    # Voltar a pedir não renderiza o PDF outra vez.
    def renderizar_pdf_espiao(*_a, **_k) -> bytes:
        raise AssertionError("não se renderiza PDF ao pedir a miniatura")

    dados = obter_miniatura_indexada(
        caminho_mini,
        renderizar_pdf=renderizar_pdf_espiao,
    )
    assert dados == b"\x89PNG\r\n\x1a\nminiatura-sintetica"
    assert len(render_chamadas) == 1

    # Pesos ausentes: erro tipado com caminho local; sem descarregar.
    pasta_vazia = tmp_path / "models_vazios"
    pasta_vazia.mkdir()
    with pytest.raises(PesosEmbeddingAusentes) as excinfo:
        carregar_modelo(raiz_modelos=pasta_vazia)
    erro = excinfo.value
    esperado = str(caminho_pesos(pasta_vazia))
    assert erro.caminho_manual == esperado
    assert "embeddinggemma" in erro.caminho_manual.casefold()
