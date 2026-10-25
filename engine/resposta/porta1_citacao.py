"""Porta 1 — a frase tem de acabar com [n] de um trecho do pacote."""

from __future__ import annotations

import re
from typing import Sequence

from engine.resposta.tipos import CandidatoCitado, TrechoPacote

# Citação no fim da frase: … [n]  (n ≥ 1)
_RE_CITACAO_FINAL = re.compile(r"\[(\d+)\]\s*$")


def passar_porta1(
    frase: str,
    pacote: Sequence[TrechoPacote],
) -> CandidatoCitado | None:
    """Aceita só frases que terminam com [n] presente no pacote desta procura."""
    texto = frase.strip()
    if not texto:
        return None
    m = _RE_CITACAO_FINAL.search(texto)
    if m is None:
        return None
    n = int(m.group(1))
    if n < 1:
        return None
    indices = {t.n for t in pacote}
    if n not in indices:
        return None
    return CandidatoCitado(texto=texto, n=n)
