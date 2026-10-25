"""Porta 2 — fidelidade frase↔trecho citado via juiz (mesmo limiar visível)."""

from __future__ import annotations

from typing import Protocol, Sequence

from engine.pesquisa.limiar import limiar_visivel
from engine.resposta.tipos import CandidatoCitado, FraseAceite, TrechoPacote


class _SessaoAvaliavel(Protocol):
    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]: ...


def _trecho_por_n(pacote: Sequence[TrechoPacote], n: int) -> TrechoPacote | None:
    for t in pacote:
        if t.n == n:
            return t
    return None


def passar_porta2(
    candidato: CandidatoCitado,
    pacote: Sequence[TrechoPacote],
    *,
    sessao: _SessaoAvaliavel,
    tau: float | None = None,
) -> FraseAceite | None:
    """Compara a frase com o trecho [n]; sai se score < limiar de fidelidade."""
    trecho = _trecho_por_n(pacote, candidato.n)
    if trecho is None:
        return None
    # O juiz pontua o par (trecho citado, frase candidata) — mesma API
    # ``avaliar(pergunta, frases)`` do motor ONNX (PLN-08).
    scores = sessao.avaliar(trecho.texto, [candidato.texto])
    if not scores:
        return None
    corte = limiar_visivel() if tau is None else float(tau)
    if float(scores[0]) < corte:
        return None
    return FraseAceite(texto=candidato.texto, n=candidato.n)
