"""Piso documentado: Python 3.11+, Node 22, 16 GB de RAM."""

from __future__ import annotations

import sys
from typing import Iterable

PYTHON_MINIMO = (3, 11)
NODE_MINIMO = 22
RAM_GB_ALVO = 16

# Frases canónicas que a documentação de arranque deve conter (REG-MOD-002).
FRASES_PISO = (
    "Python 3.11",
    "Node 22",
    "16 GB",
)


class PisoInsuficiente(RuntimeError):
    """Versão de Python abaixo do piso — falha observável, não corrida calada."""

    def __init__(self, versao: tuple[int, ...]) -> None:
        self.versao = versao
        super().__init__(
            f"Python {versao[0]}.{versao[1]} abaixo do piso "
            f"{PYTHON_MINIMO[0]}.{PYTHON_MINIMO[1]}+. "
            "Actualiza o interpretador antes de correr a Lente."
        )


def verificar_piso(
    *,
    versao_python: tuple[int, ...] | None = None,
) -> None:
    """Falha se a versão de Python estiver abaixo de 3.11."""
    actual = versao_python if versao_python is not None else sys.version_info[:2]
    if actual < PYTHON_MINIMO:
        raise PisoInsuficiente(actual)


def documentacao_declara_piso(textos: Iterable[str]) -> bool:
    """Verdadeiro se o conjunto de textos cobre o piso completo."""
    junto = "\n".join(textos)
    return all(frase in junto for frase in FRASES_PISO)
