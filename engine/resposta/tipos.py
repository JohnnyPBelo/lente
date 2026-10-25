"""Tipos do pacote de prosa: trechos, frases aceites, excertos e miniaturas."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrechoPacote:
    """Trecho aprovado pelo juiz nesta procura (índice [n] 1-based)."""

    n: int
    ficheiro: str
    pagina: int | None
    texto: str
    documento_id: str
    offset_inicio: int | None = None
    offset_fim: int | None = None


@dataclass(frozen=True)
class PaginaAberta:
    """Página do leitor a incluir quando a pergunta é sobre ela."""

    documento_id: str
    pagina: int
    texto: str
    ficheiro: str | None = None


@dataclass(frozen=True)
class FraseAceite:
    """Frase que passou as duas portas."""

    texto: str
    n: int


@dataclass(frozen=True)
class CandidatoCitado:
    """Frase que passou a porta 1 (citação [n] no pacote)."""

    texto: str
    n: int


@dataclass(frozen=True)
class Miniatura:
    documento_id: str
    pagina: int | None = None
    caminho: str | None = None


@dataclass(frozen=True)
class Excerto:
    n: int
    documento_id: str
    pagina: int | None
    texto: str
    offset_inicio: int | None = None
    offset_fim: int | None = None
