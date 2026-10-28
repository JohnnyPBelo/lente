"""Textos grandes: blocos FTS + frases relacionais sem commits por frase (#69)."""

from __future__ import annotations

import time
from pathlib import Path

from engine.ingestao.indexar_minimo import indexar_texto_fts
from engine.ingestao.registo import registar_texto
from engine.pesquisa.fts import procurar_fts


def test_indexar_texto_grande_em_blocos(ligacao, tmp_path: Path) -> None:
    """Gutenberg-sized texto: vários blocos FTS, frases na tabela, <2s locais."""
    # ~120k chars com pontuação → milhares de frases potenciais.
    frase = (
        "Era uma vez um documento longo com prova lexical CVE-2099-0042 no meio. "
    )
    texto = (frase * 2500).strip()
    assert len(texto) > 80_000

    destino = tmp_path / "grande.txt"
    registo = registar_texto(ligacao, texto, destino)

    t0 = time.perf_counter()
    n_frases = indexar_texto_fts(
        ligacao,
        documento_id=registo.id,
        texto=texto,
        pasta_miniaturas=tmp_path / "thumbs",
    )
    decorrido = time.perf_counter() - t0

    n_blocos = ligacao.execute(
        "SELECT COUNT(*) FROM blocos WHERE documento_id = ?", (registo.id,)
    ).fetchone()[0]
    n_fts_bloco = ligacao.execute(
        "SELECT COUNT(*) FROM fts_texto WHERE documento_id = ? AND origem = 'bloco'",
        (registo.id,),
    ).fetchone()[0]
    n_fts_frase = ligacao.execute(
        "SELECT COUNT(*) FROM fts_texto WHERE documento_id = ? AND origem = 'frase'",
        (registo.id,),
    ).fetchone()[0]

    assert n_frases >= 100
    assert n_blocos >= 2
    assert n_fts_bloco == n_blocos
    # Retrieval FTS = blocos; frases só na tabela relacional.
    assert n_fts_frase == 0
    assert decorrido < 2.0, f"indexação demasiado lenta: {decorrido:.3f}s"

    hits = procurar_fts(ligacao, "CVE-2099-0042")
    assert any(h.documento_id == registo.id for h in hits)
