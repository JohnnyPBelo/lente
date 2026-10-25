"""Regressão REG-BUS-005: cosseno exacto 256d sem índice aproximado."""

from __future__ import annotations

import math

from tests.pesquisa.conftest import semear_bloco

from engine.pesquisa.vec import (
    DIMENSOES,
    guardar_vector,
    normalizar,
    procurar_cosseno,
    tipo_indice,
)


def _eixo(i: int) -> list[float]:
    """Vector unitário no eixo ``i`` (resto a zero), 256-d."""
    v = [0.0] * DIMENSOES
    v[i % DIMENSOES] = 1.0
    return v


def test_reg_bus_005(ligacao) -> None:
    """Consulta idêntica ao #2 devolve #2 em primeiro com cosseno ≈ 1; ninguém omitido."""
    assert tipo_indice() == "exacto"
    assert "ann" not in tipo_indice().casefold()
    assert "vec1" not in tipo_indice().casefold()

    ids: list[int] = []
    for i in range(3):
        bloco_id, _doc, hash_id = semear_bloco(
            ligacao,
            f"bloco {i}",
            caminho=f"/tmp/cos-{i}.txt",
        )
        guardar_vector(
            ligacao,
            bloco_id=bloco_id,
            hash_id=hash_id,
            vector=normalizar(_eixo(i + 1)),
        )
        ids.append(bloco_id)

    consulta = normalizar(_eixo(2))  # idêntico ao segundo
    resultados = procurar_cosseno(ligacao, consulta, limite=10)

    assert len(resultados) == 3
    assert {r.bloco_id for r in resultados} == set(ids)
    assert resultados[0].bloco_id == ids[1]
    assert math.isclose(resultados[0].cosseno, 1.0, rel_tol=0, abs_tol=1e-5)
