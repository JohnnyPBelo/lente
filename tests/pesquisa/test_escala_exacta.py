"""Regressão REG-DES-001: escala com milhares de vectores, cosseno exacto."""

from __future__ import annotations

from engine.pesquisa.vec import (
    DIMENSOES,
    guardar_vector,
    normalizar,
    procurar_cosseno,
    tipo_indice,
)


def test_reg_des_001(ligacao) -> None:
    """≥2000 vectores sintéticos: o vizinho exacto devolve-se; sem ramo ANN."""
    assert tipo_indice() == "exacto"
    n = 2000
    alvo_ordem = 1234

    # Um único documento com muitos blocos (mais barato que 2000 documentos).
    agora = "2026-10-25T00:00:00Z"
    ligacao.execute(
        "INSERT INTO documentos ("
        "caminho, titulo, tipo, sha256, estado, criado_em, actualizado_em"
        ") VALUES ('/tmp/escala.txt', 'escala', 'txt', 'esc', 'ok', ?, ?)",
        (agora, agora),
    )
    documento_id = int(ligacao.execute("SELECT last_insert_rowid()").fetchone()[0])
    ligacao.execute(
        "INSERT INTO documento_hashes (documento_id, sha256, visto_em, activa) "
        "VALUES (?, 'esc', ?, 1)",
        (documento_id, agora),
    )
    hash_id = int(ligacao.execute("SELECT last_insert_rowid()").fetchone()[0])

    alvo_bloco: int | None = None
    for i in range(n):
        texto = f"bloco escala {i}"
        ligacao.execute(
            "INSERT INTO blocos ("
            "documento_id, hash_id, ordem, texto, offset_inicio, offset_fim, tokens_aprox"
            ") VALUES (?, ?, ?, ?, 0, ?, 1)",
            (documento_id, hash_id, i, texto, len(texto)),
        )
        bloco_id = int(ligacao.execute("SELECT last_insert_rowid()").fetchone()[0])
        v = [0.0] * DIMENSOES
        v[i % DIMENSOES] = 1.0 + (i / n)
        if i == alvo_ordem:
            v = [0.0] * DIMENSOES
            v[0] = 42.0
            alvo_bloco = bloco_id
        guardar_vector(
            ligacao,
            bloco_id=bloco_id,
            hash_id=hash_id,
            vector=normalizar(v),
        )
    ligacao.commit()
    assert alvo_bloco is not None

    consulta = normalizar([42.0] + [0.0] * (DIMENSOES - 1))
    resultados = procurar_cosseno(ligacao, consulta, limite=5)
    assert resultados
    assert resultados[0].bloco_id == alvo_bloco
    assert tipo_indice() == "exacto"
