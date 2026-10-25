"""LoRA rank 8 do juiz: só com slot livre; PyTorch entra e sai."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any, Protocol

from engine.escalonador.nucleos import LORA_MAX
from engine.escalonador.slot import SlotPesado
from engine.feedback.registar import listar_pares
from engine.feedback.validar_troca import avaliar_holdout

RANK = 8
LEARNING_RATE = 1e-4
PULL_TO_BASE = 0.01


@dataclass
class EstadoTorch:
    """Observabilidade da presença do stack PyTorch do juiz."""

    presente: bool = False
    historico: list[bool] = field(default_factory=list)


class Treinador(Protocol):
    """Contrato injectável: testes usam double; produção pode ligar PyTorch."""

    torch_presente: bool

    def carregar_pytorch(self) -> None: ...

    def libertar(self) -> None: ...

    def treinar(
        self,
        pares: list[dict[str, Any]],
        *,
        rank: int,
        learning_rate: float,
        pull_to_base: float,
        nucleos: int,
    ) -> dict[str, Any]: ...


def libertar_torch(
    treinador: Treinador | None = None,
    *,
    estado_torch: EstadoTorch | None = None,
) -> None:
    """Garante que o PyTorch do juiz sai da memória."""
    if treinador is not None:
        treinador.libertar()
    if estado_torch is not None:
        estado_torch.presente = False
        estado_torch.historico.append(False)


def treinar_lora(
    ligacao: sqlite3.Connection,
    *,
    slot: SlotPesado,
    treinador: Treinador,
    estado_torch: EstadoTorch | None = None,
    nucleos: int = LORA_MAX,
    holdout_fraccao: float = 0.2,
) -> dict[str, Any]:
    """Treina LoRA do juiz no slot ``lora``; rejeita se o holdout piorar.

    Não treina E2B nem EmbeddingGemma. Durante o treino a procura continua
    a usar ``slot.onnx_activo()`` (ONNX anterior) até um export aceite.
    """
    if nucleos > LORA_MAX:
        nucleos = LORA_MAX

    pares = listar_pares(ligacao)
    if not pares:
        return {
            "aceite": False,
            "adaptador_id": None,
            "motivo": "sem_pares",
        }

    estado = estado_torch or EstadoTorch()

    with slot.antes_de_lora():
        # ONNX em uso pela procura permanece o anterior.
        onnx_durante = slot.onnx_activo()
        treinador.carregar_pytorch()
        estado.presente = True
        estado.historico.append(True)
        try:
            # Holdout: últimos N% como validação (ordem de inserção).
            if 0.0 < holdout_fraccao < 1.0 and len(pares) >= 2:
                corte = max(1, int(len(pares) * (1.0 - holdout_fraccao)))
                treino, holdout = pares[:corte], pares[corte:]
            else:
                treino, holdout = pares, []

            metricas = treinador.treinar(
                treino,
                rank=RANK,
                learning_rate=LEARNING_RATE,
                pull_to_base=PULL_TO_BASE,
                nucleos=nucleos,
            )
            base = float(metricas.get("metrica_holdout_base", 0.0))
            nova = float(metricas.get("metrica_holdout", base))
            if holdout and not avaliar_holdout(base, nova):
                return {
                    "aceite": False,
                    "adaptador_id": metricas.get("adaptador_id"),
                    "motivo": "holdout_pior",
                    "onnx_activo": onnx_durante,
                }
            return {
                "aceite": True,
                "adaptador_id": metricas.get("adaptador_id"),
                "motivo": "ok",
                "onnx_activo": onnx_durante,
                "n_treino": len(treino),
                "n_holdout": len(holdout),
            }
        finally:
            libertar_torch(treinador, estado_torch=estado)
