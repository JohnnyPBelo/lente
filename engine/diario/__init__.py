"""Diário local append-only: procuras, aberturas, feedback e fechos."""

from __future__ import annotations

from engine.diario.escrever import (
    TIPOS_ACEITES,
    TipoDiarioInvalido,
    acrescentar,
    registar_abertura,
    registar_fecho_dossier,
    registar_feedback,
    registar_procura,
)
from engine.diario.ler import ler_diario

__all__ = [
    "TIPOS_ACEITES",
    "TipoDiarioInvalido",
    "acrescentar",
    "ler_diario",
    "registar_abertura",
    "registar_fecho_dossier",
    "registar_feedback",
    "registar_procura",
]
