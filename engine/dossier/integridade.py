"""Comparar SHA-256 actual em disco com a fotografia do dossier."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.ingestao.hash import sha256_ficheiro
from engine.ingestao.tipos import FicheiroInexistente


def sha_actual(caminho: str | Path) -> str | None:
    """SHA-256 actual do ficheiro, ou ``None`` se não existir no disco."""
    try:
        return sha256_ficheiro(caminho)
    except FicheiroInexistente:
        return None


def fonte_alterada(ficheiros: list[dict[str, Any]]) -> bool:
    """Verdadeiro se algum ficheiro da fotografia divergir do disco."""
    for entrada in ficheiros:
        caminho = entrada.get("caminho")
        esperado = entrada.get("sha256")
        if not caminho or not esperado:
            continue
        actual = sha_actual(caminho)
        if actual is None or actual != esperado:
            return True
    return False


def ficheiros_com_fonte_alterada(
    ficheiros: list[dict[str, Any]],
) -> list[str]:
    """Caminhos cuja fotografia já não coincide com os bytes em disco."""
    alterados: list[str] = []
    for entrada in ficheiros:
        caminho = entrada.get("caminho")
        esperado = entrada.get("sha256")
        if not caminho or not esperado:
            continue
        actual = sha_actual(caminho)
        if actual is None or actual != esperado:
            alterados.append(str(caminho))
    return alterados
