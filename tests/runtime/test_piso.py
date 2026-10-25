"""Regressão REG-MOD-002: piso Python 3.11+ / Node 22 / 16 GB."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.runtime.piso import (
    FRASES_PISO,
    NODE_MINIMO,
    PYTHON_MINIMO,
    RAM_GB_ALVO,
    PisoInsuficiente,
    documentacao_declara_piso,
    verificar_piso,
)


def test_reg_mod_002() -> None:
    """Documentação declara o piso; Python abaixo falha de forma observável."""
    assert PYTHON_MINIMO == (3, 11)
    assert NODE_MINIMO == 22
    assert RAM_GB_ALVO == 16

    raiz = Path(__file__).resolve().parents[2]
    textos = [
        (raiz / "README.md").read_text(encoding="utf-8"),
        (raiz / "docs" / "desenvolvimento" / "ambiente.md").read_text(
            encoding="utf-8"
        ),
    ]
    assert documentacao_declara_piso(textos)
    for frase in FRASES_PISO:
        assert any(frase in t for t in textos)

    # Abaixo do piso: falha (não segue calado).
    with pytest.raises(PisoInsuficiente) as contexto:
        verificar_piso(versao_python=(3, 10))
    assert "3.10" in str(contexto.value)
    assert "3.11" in str(contexto.value)

    # No piso ou acima: ok.
    verificar_piso(versao_python=(3, 11))
    verificar_piso(versao_python=(3, 12))
