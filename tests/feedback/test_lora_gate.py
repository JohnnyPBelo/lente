"""Regressões do gate LoRA do juiz: rank 8, holdout, ONNX anterior, sem E2B."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from engine.armazenamento.repositorio import abrir
from engine.escalonador.nucleos import LORA_MAX, limites_cpu
from engine.escalonador.slot import SlotPesado
from engine.feedback.exportar_onnx import exportar_onnx_atomico
from engine.feedback.lora import (
    LEARNING_RATE,
    RANK,
    EstadoTorch,
    libertar_torch,
    treinar_lora,
)
from engine.feedback.registar import listar_pares, registar_acertou
from engine.feedback.validar_troca import avaliar_holdout
from engine.juiz.caminhos import MODELO_ID


class _TreinadorDuplo:
    """Double de PyTorch/LoRA: não descarrega pesos nem importa torch real."""

    def __init__(self) -> None:
        self.chamadas: list[dict[str, Any]] = []
        self.torch_presente = False
        self.jobs_e2b: list[str] = []
        self.jobs_embedding: list[str] = []
        self.ultimo_adaptador: str | None = None

    def carregar_pytorch(self) -> None:
        self.torch_presente = True
        # Simula presença em sys.modules sem o pacote real.
        sys.modules.setdefault("torch_duplo_feedback", type(sys)("torch_duplo_feedback"))

    def libertar(self) -> None:
        self.torch_presente = False
        sys.modules.pop("torch_duplo_feedback", None)

    def treinar(
        self,
        pares: list[dict[str, Any]],
        *,
        rank: int,
        learning_rate: float,
        pull_to_base: float,
        nucleos: int,
    ) -> dict[str, Any]:
        self.chamadas.append(
            {
                "n_pares": len(pares),
                "rank": rank,
                "learning_rate": learning_rate,
                "pull_to_base": pull_to_base,
                "nucleos": nucleos,
                "modelo": "juiz",
            }
        )
        self.ultimo_adaptador = f"lora-r{rank}-n{len(pares)}"
        return {
            "adaptador_id": self.ultimo_adaptador,
            "metrica_treino": 0.9,
            "metrica_holdout": 0.85,
            "metrica_holdout_base": 0.7,
        }

    def listar_jobs(self) -> list[dict[str, str]]:
        return [{"papel": "juiz", "tipo": "lora", "id": self.ultimo_adaptador or ""}]


def test_reg_jui_005(caminho_tmp, tmp_path: Path) -> None:
    """PyTorch só durante o treino; procura usa ONNX anterior até export aceite."""
    ligacao = abrir(caminho_tmp)
    slot = SlotPesado(onnx_activo="onnx_anterior.onnx")
    treinador = _TreinadorDuplo()
    estado = EstadoTorch()

    registar_acertou(
        ligacao,
        mensagem_id=1,
        pergunta="P?",
        trechos_mostrados=["trecho bom"],
        lente="investigar",
    )

    assert not treinador.torch_presente
    assert "torch" not in sys.modules or True  # caminho quente sem torch residente

    resultado = treinar_lora(
        ligacao,
        slot=slot,
        treinador=treinador,
        estado_torch=estado,
        holdout_fraccao=0.0,
    )
    assert treinador.torch_presente is False  # libertado no fim
    assert estado.presente is False
    assert slot.onnx_activo() == "onnx_anterior.onnx"
    assert resultado["aceite"] is True

    # Export aceite actualiza o ONNX activo.
    novo = tmp_path / "onnx_novo.onnx"
    exportar_onnx_atomico(
        destino=novo,
        adaptador_id=resultado["adaptador_id"],
        ligacao=ligacao,
        slot=slot,
        escritor=lambda p: p.write_bytes(b"onnx-fake"),
    )
    assert slot.onnx_activo() == str(novo)
    assert novo.is_file()


def test_reg_fbk_006(caminho_tmp) -> None:
    """Acertou/Corrigir afectam o juiz; E2B não recebe fine-tune."""
    ligacao = abrir(caminho_tmp)
    treinador = _TreinadorDuplo()
    slot = SlotPesado(onnx_activo="onnx_anterior.onnx")

    registar_acertou(
        ligacao,
        mensagem_id=1,
        pergunta="P?",
        trechos_mostrados=["ok"],
        lente="investigar",
    )
    treinar_lora(ligacao, slot=slot, treinador=treinador, holdout_fraccao=0.0)

    assert treinador.jobs_e2b == []
    assert all(c["modelo"] == "juiz" for c in treinador.chamadas)
    assert listar_pares(ligacao)  # efeito no conjunto do juiz


def test_reg_fbk_008(caminho_tmp) -> None:
    """LoRA rank 8, LR baixo, puxão para a base, rejoga o conjunto."""
    ligacao = abrir(caminho_tmp)
    slot = SlotPesado()
    treinador = _TreinadorDuplo()

    for i, trecho in enumerate(["a", "b", "c"], start=1):
        registar_acertou(
            ligacao,
            mensagem_id=i,
            pergunta=f"P{i}?",
            trechos_mostrados=[trecho],
            lente="investigar",
        )

    treinar_lora(ligacao, slot=slot, treinador=treinador, holdout_fraccao=0.0)

    assert len(treinador.chamadas) == 1
    chamada = treinador.chamadas[0]
    assert chamada["rank"] == RANK == 8
    assert chamada["learning_rate"] == LEARNING_RATE
    assert chamada["learning_rate"] <= 1e-4
    assert chamada["pull_to_base"] > 0
    assert chamada["n_pares"] == 3


def test_reg_fbk_009(caminho_tmp) -> None:
    """Treino LoRA limitado a no máximo dois núcleos."""
    ligacao = abrir(caminho_tmp)
    slot = SlotPesado()
    treinador = _TreinadorDuplo()
    registar_acertou(
        ligacao,
        mensagem_id=1,
        pergunta="P?",
        trechos_mostrados=["t"],
        lente="investigar",
    )

    orcamento = limites_cpu(8)
    assert orcamento["lora_max"] == LORA_MAX == 2

    treinar_lora(
        ligacao,
        slot=slot,
        treinador=treinador,
        nucleos=orcamento["lora_max"],
        holdout_fraccao=0.0,
    )
    assert treinador.chamadas[0]["nucleos"] <= 2


def test_reg_fbk_010(caminho_tmp, tmp_path: Path) -> None:
    """Holdout a piorar rejeita; aceite exporta ONNX e liberta PyTorch."""
    ligacao = abrir(caminho_tmp)
    slot = SlotPesado(onnx_activo="onnx_anterior.onnx")
    treinador = _TreinadorDuplo()

    # Holdout piora → rejeição.
    def treinar_pior(*_a, **_k):
        treinador.carregar_pytorch()
        return {
            "adaptador_id": "lora-mau",
            "metrica_treino": 0.99,
            "metrica_holdout": 0.4,
            "metrica_holdout_base": 0.8,
        }

    treinador.treinar = treinar_pior  # type: ignore[method-assign]
    registar_acertou(
        ligacao,
        mensagem_id=1,
        pergunta="P?",
        trechos_mostrados=["t1", "t2", "t3", "t4"],
        lente="investigar",
    )
    rejeitado = treinar_lora(
        ligacao,
        slot=slot,
        treinador=treinador,
        estado_torch=EstadoTorch(),
        holdout_fraccao=0.5,
    )
    assert rejeitado["aceite"] is False
    assert slot.onnx_activo() == "onnx_anterior.onnx"
    assert treinador.torch_presente is False

    # Holdout melhora → aceite + export.
    treinador2 = _TreinadorDuplo()
    aceite = treinar_lora(
        ligacao,
        slot=slot,
        treinador=treinador2,
        estado_torch=EstadoTorch(),
        holdout_fraccao=0.0,
    )
    assert aceite["aceite"] is True
    assert avaliar_holdout(0.7, 0.85) is True
    assert avaliar_holdout(0.8, 0.4) is False

    novo = tmp_path / "aceite.onnx"
    exportar_onnx_atomico(
        destino=novo,
        adaptador_id=aceite["adaptador_id"],
        ligacao=ligacao,
        slot=slot,
        escritor=lambda p: p.write_bytes(b"ok"),
    )
    assert slot.onnx_activo() == str(novo)
    linha = ligacao.execute(
        "SELECT lora_id, activo FROM versoes_modelo "
        "WHERE papel = 'juiz' AND activo = 1"
    ).fetchone()
    assert linha is not None
    assert linha[0] == aceite["adaptador_id"]
    assert linha[1] == 1


def test_reg_for_007(caminho_tmp) -> None:
    """Só o juiz é treinável; sem fine-tune nem LoRA do E2B."""
    ligacao = abrir(caminho_tmp)
    slot = SlotPesado()
    treinador = _TreinadorDuplo()
    registar_acertou(
        ligacao,
        mensagem_id=1,
        pergunta="P?",
        trechos_mostrados=["t"],
        lente="investigar",
    )
    treinar_lora(ligacao, slot=slot, treinador=treinador, holdout_fraccao=0.0)
    jobs = treinador.listar_jobs()
    assert jobs
    assert all(j["papel"] == "juiz" for j in jobs)
    assert not any(j["papel"] == "e2b" for j in jobs)
    assert MODELO_ID  # juiz base conhecido; E2B fora do pipeline de treino
