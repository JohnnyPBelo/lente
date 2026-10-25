"""Pipeline das duas portas; sem prosa provisória no resultado observável."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Sequence

from engine.resposta.porta1_citacao import passar_porta1
from engine.resposta.porta2_fiel import passar_porta2
from engine.resposta.tipos import Excerto, FraseAceite, Miniatura, TrechoPacote

AVISO_VAZIO = "nenhuma_frase_acima_do_limiar"


class _SessaoAvaliavel(Protocol):
    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]: ...


@dataclass
class ResultadoParcial:
    """Estado observável enquanto as portas correm.

    Miniaturas/excertos podem existir; ``frases`` fica vazio até
    ``portas_concluidas``. Nunca há prosa provisória a apagar depois.
    """

    miniaturas: list[Miniatura] = field(default_factory=list)
    excertos: list[Excerto] = field(default_factory=list)
    candidatos_brutos: list[str] = field(default_factory=list)
    portas_concluidas: bool = False
    frases: list[FraseAceite] = field(default_factory=list)
    prosa_provisoria: bool = False
    vazio: bool = False
    aviso_vazio: str | None = None


@dataclass
class ResultadoResposta:
    """Mensagem fechada: só frases que passaram as duas portas."""

    frases: list[FraseAceite]
    excertos: list[Excerto]
    miniaturas: list[Miniatura]
    portas_concluidas: bool = True
    prosa_provisoria: bool = False
    vazio: bool = False
    aviso_vazio: str | None = None


def filtrar_frases(
    candidatos: Sequence[str],
    *,
    pacote: Sequence[TrechoPacote],
    sessao: _SessaoAvaliavel,
    miniaturas: Sequence[Miniatura] | None = None,
    excertos: Sequence[Excerto] | None = None,
    tau: float | None = None,
) -> ResultadoResposta:
    """Corre porta 1 e porta 2; só emite frases aceites no fim."""
    aceites: list[FraseAceite] = []
    for frase in candidatos:
        cand = passar_porta1(frase, pacote)
        if cand is None:
            continue
        fiel = passar_porta2(cand, pacote, sessao=sessao, tau=tau)
        if fiel is None:
            continue
        aceites.append(fiel)

    return ResultadoResposta(
        frases=aceites,
        excertos=list(excertos or []),
        miniaturas=list(miniaturas or []),
        portas_concluidas=True,
        prosa_provisoria=False,
        vazio=False,
        aviso_vazio=None,
    )


def fechar_mensagem(resultado: ResultadoResposta) -> ResultadoResposta:
    """Se zero frases: mantém excertos/miniaturas ou marca aviso de vazio."""
    if resultado.frases:
        return resultado
    tem_prova = bool(resultado.excertos or resultado.miniaturas)
    if tem_prova:
        return ResultadoResposta(
            frases=[],
            excertos=resultado.excertos,
            miniaturas=resultado.miniaturas,
            portas_concluidas=True,
            prosa_provisoria=False,
            vazio=False,
            aviso_vazio=None,
        )
    return ResultadoResposta(
        frases=[],
        excertos=[],
        miniaturas=[],
        portas_concluidas=True,
        prosa_provisoria=False,
        vazio=True,
        aviso_vazio=AVISO_VAZIO,
    )
