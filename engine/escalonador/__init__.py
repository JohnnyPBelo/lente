"""Escalonador: um trabalho pesado de cada vez e orçamento de núcleos."""

from __future__ import annotations

from pathlib import Path

from engine.escalonador.estados import (
    ESTADOS_OBSERVAVEIS,
    Estado,
    FilaOcupada,
)
from engine.escalonador.fila_ingestao import FilaIngestao
from engine.escalonador.nucleos import limites_cpu
from engine.escalonador.slot import SlotPesado, gravar_feedback_imediato


def obter_miniatura(
    caminho: Path | str,
    *,
    renderizar_pdf=None,
) -> bytes:
    """Devolve a miniatura gravada na indexação; nunca re-renderiza o PDF."""
    del renderizar_pdf  # o orçamento proíbe render no hover
    return Path(caminho).read_bytes()


__all__ = [
    "ESTADOS_OBSERVAVEIS",
    "Estado",
    "FilaIngestao",
    "FilaOcupada",
    "SlotPesado",
    "gravar_feedback_imediato",
    "limites_cpu",
    "obter_miniatura",
]
