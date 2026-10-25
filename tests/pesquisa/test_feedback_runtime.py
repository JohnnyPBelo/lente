"""Regressão REG-FBK-007: boost/penalização imediata sem injectar no escritor."""

from __future__ import annotations

from engine.pesquisa.feedback_runtime import (
    CorrecaoRecente,
    material_para_escritor,
    reordenar_por_feedback,
)


def test_reg_fbk_007() -> None:
    """Confirmados sobem, rejeitados descem; texto de feedback fora do escritor."""
    pergunta = "qual o controlo de acessos na norma?"
    candidatos = ["neutro", "rejeitado", "confirmado", "outro"]
    correcoes = [
        CorrecaoRecente(
            pergunta="qual o controlo de acessos?",
            trecho_id="confirmado",
            positivo=True,
        ),
        CorrecaoRecente(
            pergunta="controlo de acessos na norma",
            trecho_id="rejeitado",
            positivo=False,
        ),
        # Pergunta diferente: não mexe
        CorrecaoRecente(
            pergunta="receita de bolo de chocolate",
            trecho_id="outro",
            positivo=True,
        ),
    ]

    ordenados = reordenar_por_feedback(
        candidatos, pergunta=pergunta, correcoes=correcoes
    )

    assert ordenados.index("confirmado") < ordenados.index("neutro")
    assert ordenados.index("neutro") < ordenados.index("rejeitado")
    # Não injecta ids novos
    assert set(ordenados) == set(candidatos)
    # «outro» não sobe (pergunta dissimilar)
    assert ordenados.index("outro") > ordenados.index("confirmado")

    # Texto de feedback não entra no prompt do escritor
    assert material_para_escritor(correcoes) == []
    assert material_para_escritor([]) == []
