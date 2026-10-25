"""Regressão REG-ING-010: blocos ~500/overlap 50 e frases com offsets/caixas."""

from __future__ import annotations

from pathlib import Path

from engine.ingestao.caixas import Caixa
from engine.embeddings.cortar import (
    MARGEM_TOKENS,
    OVERLAP_TOKENS,
    TOKENS_BLOCO,
    cortar_blocos,
)
from engine.embeddings.frases import segmentar_frases

FIXTORES = Path(__file__).resolve().parents[1] / "fixtures" / "embeddings"


class TokenizadorPalavras:
    """Double leve: uma palavra = um token, com offsets de carácter."""

    def offsets_tokens(self, texto: str) -> list[tuple[int, int]]:
        offsets: list[tuple[int, int]] = []
        inicio = None
        for indice, ch in enumerate(texto):
            if ch.isspace():
                if inicio is not None:
                    offsets.append((inicio, indice))
                    inicio = None
            else:
                if inicio is None:
                    inicio = indice
        if inicio is not None:
            offsets.append((inicio, len(texto)))
        return offsets

    def contar(self, texto: str) -> int:
        return len(self.offsets_tokens(texto))


def test_reg_ing_010() -> None:
    """Texto >600 tokens → ≥2 blocos ≤~500 com overlap ≈50; frases com offsets."""
    texto = (FIXTORES / "paragrafo_longo.txt").read_text(encoding="utf-8")
    tokenizador = TokenizadorPalavras()
    assert tokenizador.contar(texto) > 600

    blocos = cortar_blocos(texto, tokenizador=tokenizador)
    assert len(blocos) >= 2

    for bloco in blocos:
        assert bloco.tokens_aprox <= TOKENS_BLOCO + MARGEM_TOKENS
        assert bloco.offset_inicio < bloco.offset_fim
        assert texto[bloco.offset_inicio : bloco.offset_fim] == bloco.texto

    # Sobreposição ≈50 tokens entre o fim do bloco i e o início do i+1.
    for anterior, seguinte in zip(blocos, blocos[1:]):
        tokens_fim = tokenizador.offsets_tokens(anterior.texto)
        tokens_inicio = tokenizador.offsets_tokens(seguinte.texto)
        n = min(OVERLAP_TOKENS, len(tokens_fim), len(tokens_inicio))
        assert n >= OVERLAP_TOKENS - MARGEM_TOKENS
        trecho_fim = anterior.texto[tokens_fim[-n][0] : tokens_fim[-1][1]]
        trecho_inicio = seguinte.texto[tokens_inicio[0][0] : tokens_inicio[n - 1][1]]
        assert trecho_fim == trecho_inicio

    # Frases: offsets; caixas quando o formato as traz.
    amostra = (
        "Primeira frase sintetica do controlo. "
        "Segunda frase com prova na pagina."
    )
    caixa = Caixa(pagina=1, x=10.0, y=20.0, largura=100.0, altura=12.0)
    frases = segmentar_frases(
        amostra,
        caixas_por_intervalo=[
            (0, amostra.index("."), [caixa]),
        ],
    )
    assert len(frases) >= 2
    for frase in frases:
        assert frase.offset_inicio < frase.offset_fim
        assert amostra[frase.offset_inicio : frase.offset_fim] == frase.texto
    assert frases[0].caixas == [caixa]
    assert frases[1].caixas == []
