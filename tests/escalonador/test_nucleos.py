"""Regressão REG-MOD-003: ≥2 núcleos livres; E2B ≤ nproc−2."""

from __future__ import annotations

from engine.escalonador.nucleos import limites_cpu


def test_reg_mod_003() -> None:
    """Para 4, 8 e 16 núcleos: livres ≥2 e E2B em 2, 6 e 14."""
    esperado = {
        4: (2, 2, 2),
        8: (2, 6, 2),
        16: (2, 14, 2),
    }
    for nproc, (livres, e2b, lora) in esperado.items():
        limites = limites_cpu(nproc)
        assert limites["livres_minimos"] == livres
        assert limites["e2b_max"] == e2b
        assert limites["lora_max"] == lora
        assert limites["e2b_max"] == nproc - limites["livres_minimos"]
        assert limites["livres_minimos"] >= 2
