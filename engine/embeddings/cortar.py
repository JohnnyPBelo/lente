"""Corte de texto em blocos EmbeddingGemma (~500 tokens, overlap 50)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

# Alvo do produto (ADR-012). A margem documenta o desvio aceite nos testes.
TOKENS_BLOCO = 500
OVERLAP_TOKENS = 50
MARGEM_TOKENS = 16


class TokenizadorOffsets(Protocol):
    """Tokenizador injectável: offsets de carácter por token (exclusive no fim)."""

    def offsets_tokens(self, texto: str) -> list[tuple[int, int]]: ...


@dataclass(frozen=True)
class BlocoCortado:
    """Um bloco pronto a embutir, com offsets no texto do documento."""

    texto: str
    offset_inicio: int
    offset_fim: int
    tokens_aprox: int
    ordem: int


def cortar_blocos(
    texto: str,
    *,
    tokenizador: TokenizadorOffsets,
    tokens_bloco: int = TOKENS_BLOCO,
    overlap: int = OVERLAP_TOKENS,
) -> list[BlocoCortado]:
    """Parte ``texto`` em blocos de até ``tokens_bloco`` com sobreposição ``overlap``.

    Cada bloco tem no máximo ``tokens_bloco`` tokens (sem margem extra na
    produção). A ``MARGEM_TOKENS`` só documenta tolerância nos testes de
    regressão face a tokenizadores stub.
    """
    if tokens_bloco <= 0:
        raise ValueError("tokens_bloco tem de ser positivo")
    if overlap < 0 or overlap >= tokens_bloco:
        raise ValueError("overlap tem de ser >= 0 e < tokens_bloco")

    offsets = tokenizador.offsets_tokens(texto)
    if not offsets:
        return []

    blocos: list[BlocoCortado] = []
    inicio = 0
    ordem = 0
    total = len(offsets)
    passo = tokens_bloco - overlap

    while inicio < total:
        fim = min(inicio + tokens_bloco, total)
        char_inicio = offsets[inicio][0]
        char_fim = offsets[fim - 1][1]
        trecho = texto[char_inicio:char_fim]
        blocos.append(
            BlocoCortado(
                texto=trecho,
                offset_inicio=char_inicio,
                offset_fim=char_fim,
                tokens_aprox=fim - inicio,
                ordem=ordem,
            )
        )
        ordem += 1
        if fim >= total:
            break
        inicio += passo

    return blocos


__all__ = [
    "MARGEM_TOKENS",
    "OVERLAP_TOKENS",
    "TOKENS_BLOCO",
    "BlocoCortado",
    "TokenizadorOffsets",
    "cortar_blocos",
]
