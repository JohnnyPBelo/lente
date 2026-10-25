"""Regressão REG-MOD-009: EmbeddingGemma + juiz residentes; E2B é visita."""

from __future__ import annotations

from engine.runtime.residentes import (
    E2B_VISITA,
    EMBEDDING_RESIDENTE,
    JUIZ_RESIDENTE,
    dtype_embedding_cpu,
    e2b_e_residente,
    listar_residentes,
)


def test_reg_mod_009() -> None:
    """Fora da janela E2B: residentes = EmbeddingGemma + juiz; E2B não."""
    residentes = listar_residentes(e2b_a_escrever=False)
    assert EMBEDDING_RESIDENTE in residentes
    assert JUIZ_RESIDENTE in residentes
    assert E2B_VISITA not in residentes
    assert e2b_e_residente() is False

    # Mesmo durante a visita o E2B não fica na lista permanente.
    durante = listar_residentes(e2b_a_escrever=True)
    assert E2B_VISITA not in durante
    assert EMBEDDING_RESIDENTE in durante
    assert JUIZ_RESIDENTE in durante

    # Dtype float32 (REG-BUS-001 reforçado aqui).
    assert dtype_embedding_cpu() == "float32"
