"""Cópia de segurança: zip local da pasta ``data/``."""

from __future__ import annotations

from engine.backup.zip_data import PastaDataInexistente, criar_copia

__all__ = [
    "PastaDataInexistente",
    "criar_copia",
]
