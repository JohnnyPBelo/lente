"""Caminhos locais do juiz ONNX int8 e identidade do modelo."""

from __future__ import annotations

import platform
from dataclasses import dataclass
from pathlib import Path

MODELO_ID = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
FICHEIRO_AVX512 = "model_qint8_avx512_vnni.onnx"
FICHEIRO_ARM64 = "model_qint8_arm64.onnx"
QUANTIZACAO = "int8"
RUNTIME = "onnx"


@dataclass(frozen=True)
class IdentidadeJuiz:
    """Identidade fixa do decisor residente (nunca Jev, Qwen ou DeBERTa)."""

    modelo_id: str
    runtime: str
    quantizacao: str
    ficheiro_onnx: str


def ficheiro_onnx_maquina(*, arquitectura: str | None = None) -> str:
    """Escolhe o artefacto int8: arm64 ou AVX-512 VNNI (preferido em x86-64)."""
    maquina = (arquitectura or platform.machine()).lower()
    if maquina in {"arm64", "aarch64"}:
        return FICHEIRO_ARM64
    return FICHEIRO_AVX512


def pasta_juiz(raiz_modelos: Path | str | None = None) -> Path:
    """Pasta runtime dos pesos: ``models/juiz/`` (fora do git)."""
    raiz = Path(raiz_modelos) if raiz_modelos is not None else Path("models")
    return Path(raiz) / "juiz"


def caminho_onnx(
    raiz_modelos: Path | str | None = None,
    *,
    arquitectura: str | None = None,
) -> Path:
    """Caminho absoluto/relativo do ficheiro ONNX int8 para esta máquina."""
    return pasta_juiz(raiz_modelos) / ficheiro_onnx_maquina(arquitectura=arquitectura)


def identificar_modelo(*, arquitectura: str | None = None) -> IdentidadeJuiz:
    """Devolve a identidade canónica do juiz (REQ-JUI-001 / REQ-FOR-005)."""
    return IdentidadeJuiz(
        modelo_id=MODELO_ID,
        runtime=RUNTIME,
        quantizacao=QUANTIZACAO,
        ficheiro_onnx=ficheiro_onnx_maquina(arquitectura=arquitectura),
    )
