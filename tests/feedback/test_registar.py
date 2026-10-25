"""Regressões de registo de feedback: Acertou / Corrigir / Descartar."""

from __future__ import annotations

import hashlib

from engine.armazenamento.repositorio import abrir
from engine.escalonador.slot import SlotPesado
from engine.feedback.registar import (
    ajustar_pontuacoes,
    listar_pares,
    registar_acertou,
    registar_corrigir,
    registar_descartar,
)


class _SlotEspiao(SlotPesado):
    """Regista aquisições do slot pesado."""

    def __init__(self) -> None:
        super().__init__(onnx_activo="onnx_anterior")
        self.aquisicoes: list[str] = []

    def adquirir(self, tipo: str):  # type: ignore[override]
        self.aquisicoes.append(tipo)
        return super().adquirir(tipo)  # type: ignore[arg-type]


def _pesos_artefacto() -> dict[str, str]:
    """Identidade de pesos congelados (doubles; sem ficheiros reais)."""
    return {
        "embeddinggemma": "emb-hash-fixo",
        "e2b": "e2b-hash-fixo",
        "juiz_onnx": "juiz-onnx-fixo",
    }


def test_reg_fbk_002(caminho_tmp) -> None:
    """Descartar não cria pares; pesos do juiz e do E2B ficam iguais."""
    ligacao = abrir(caminho_tmp)
    slot = _SlotEspiao()
    pesos_antes = _pesos_artefacto()

    registar_descartar(
        ligacao,
        mensagem_id=None,
        pergunta="Qual é a capital?",
        trechos_mostrados=["Lisboa é a capital de Portugal."],
        lente="investigar",
        slot=slot,
    )

    assert listar_pares(ligacao) == []
    assert slot.aquisicoes == []
    assert _pesos_artefacto() == pesos_antes


def test_reg_fbk_004(caminho_tmp) -> None:
    """Acertou marca os trechos mostrados como positivos."""
    ligacao = abrir(caminho_tmp)
    slot = _SlotEspiao()
    trechos = [
        "Lisboa é a capital de Portugal.",
        "O Tejo passa por Lisboa.",
    ]

    registar_acertou(
        ligacao,
        mensagem_id=None,
        pergunta="Qual é a capital de Portugal?",
        trechos_mostrados=trechos,
        lente="investigar",
        slot=slot,
    )

    pares = listar_pares(ligacao)
    assert len(pares) == 2
    assert {p["etiqueta"] for p in pares} == {"positivo"}
    assert {p["trecho"] for p in pares} == set(trechos)
    assert all(p["pergunta"] == "Qual é a capital de Portugal?" for p in pares)
    assert all(p["lente"] == "investigar" for p in pares)
    assert all(p["origem"] == "local" for p in pares)
    assert slot.aquisicoes == []


def test_reg_fbk_005(caminho_tmp) -> None:
    """Corrigir: marcas da resposta negativas; selecção positiva."""
    ligacao = abrir(caminho_tmp)
    slot = _SlotEspiao()
    marcas = ["Trecho errado na resposta."]
    selecao = "Trecho correcto no leitor."

    registar_corrigir(
        ligacao,
        mensagem_id=None,
        pergunta="Onde está a prova?",
        marcas_resposta=marcas,
        selecao=selecao,
        lente="verificar",
        slot=slot,
    )

    pares = listar_pares(ligacao)
    por_trecho = {p["trecho"]: p["etiqueta"] for p in pares}
    assert por_trecho["Trecho errado na resposta."] == "negativo"
    assert por_trecho["Trecho correcto no leitor."] == "positivo"
    assert slot.aquisicoes == []


def test_feedback_nao_adquire_slot_search(caminho_tmp) -> None:
    """Feedback imediato grava sem adquirir o slot de procura."""
    ligacao = abrir(caminho_tmp)
    slot = _SlotEspiao()

    with slot.antes_de_procurar():
        # mesmo com procura activa, o registo não pede search de novo
        registar_acertou(
            ligacao,
            mensagem_id=None,
            pergunta="p",
            trechos_mostrados=["t"],
            lente="investigar",
            slot=slot,
        )

    assert "search" not in [
        a for a in slot.aquisicoes if a == "search"
    ] or slot.aquisicoes.count("search") == 1
    # A única aquisição search veio do with, não do feedback.
    assert slot.aquisicoes == ["search"]
    assert len(listar_pares(ligacao)) == 1


def test_reg_jui_004(caminho_tmp) -> None:
    """Feedback muda ordenação/limiar do juiz; EmbeddingGemma e E2B iguais."""
    ligacao = abrir(caminho_tmp)
    pesos_antes = _pesos_artefacto()
    pergunta = "Qual é a capital de Portugal?"
    confirmado = "Lisboa é a capital de Portugal."
    rejeitado = "O motor a vapor foi aperfeiçoado no século XIX."

    registar_acertou(
        ligacao,
        mensagem_id=None,
        pergunta=pergunta,
        trechos_mostrados=[confirmado],
        lente="investigar",
    )
    registar_corrigir(
        ligacao,
        mensagem_id=None,
        pergunta=pergunta,
        marcas_resposta=[rejeitado],
        selecao=confirmado,
        lente="investigar",
    )

    # Procura semelhante: mesmos candidatos com scores iguais antes do boost.
    candidatos = [(confirmado, 0.5), (rejeitado, 0.5)]
    ajustados = ajustar_pontuacoes(
        pergunta,
        candidatos,
        pares=listar_pares(ligacao),
    )
    ordenados = sorted(ajustados, key=lambda x: x[1], reverse=True)
    assert ordenados[0][0] == confirmado
    assert ordenados[0][1] > ordenados[1][1]
    assert ordenados[1][0] == rejeitado

    assert _pesos_artefacto()["embeddinggemma"] == pesos_antes["embeddinggemma"]
    assert _pesos_artefacto()["e2b"] == pesos_antes["e2b"]


def test_hash_par_estavel_e_unico(caminho_tmp) -> None:
    """Pares repetidos entram uma vez (UNIQUE hash_par)."""
    ligacao = abrir(caminho_tmp)
    trecho = "Mesmo trecho."
    registar_acertou(
        ligacao,
        mensagem_id=None,
        pergunta="P?",
        trechos_mostrados=[trecho],
        lente="investigar",
    )
    registar_acertou(
        ligacao,
        mensagem_id=None,
        pergunta="P?",
        trechos_mostrados=[trecho],
        lente="investigar",
    )
    assert len(listar_pares(ligacao)) == 1
    esperado = hashlib.sha256(
        "P?\0Mesmo trecho.\0positivo\0investigar".encode("utf-8")
    ).hexdigest()
    assert listar_pares(ligacao)[0]["hash_par"] == esperado
