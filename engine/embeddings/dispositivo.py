"""Dispositivo e dtypes do EmbeddingGemma: um só código; GPU só acelera."""

from __future__ import annotations

DTYPE_CPU = "float32"
DTYPE_GPU = "bfloat16"
DTYPE_PROIBIDO = "float16"


class DtypeProibido(ValueError):
    """Float16 está excluído (NaN no EmbeddingGemma — ADR-007)."""

    def __init__(self, dtype: str) -> None:
        self.dtype = dtype
        super().__init__(
            f"Dtype {dtype!r} proibido para EmbeddingGemma; "
            f"use {DTYPE_CPU} em CPU ou {DTYPE_GPU} em GPU."
        )


def escolher_dispositivo(*, tem_gpu: bool) -> str:
    """Mesmo fluxo de produto: ``cuda`` se houver GPU, senão ``cpu``."""
    return "cuda" if tem_gpu else "cpu"


def dtype_para(dispositivo: str) -> str:
    """Dtype activo para o dispositivo; nunca ``float16``."""
    nome = dispositivo.casefold()
    if nome.startswith("cuda") or nome == "gpu":
        return DTYPE_GPU
    return DTYPE_CPU


def validar_dtype(dtype: str) -> str:
    """Recusa float16/fp16; devolve o dtype canónico."""
    chave = dtype.casefold().replace("torch.", "")
    if chave in {DTYPE_PROIBIDO, "fp16", "half"}:
        raise DtypeProibido(dtype)
    if chave in {"bf16", "bfloat16"}:
        return DTYPE_GPU
    if chave in {"float32", "fp32"}:
        return DTYPE_CPU
    raise DtypeProibido(dtype)


def fluxo_unico() -> bool:
    """Confirma que não há segundo modo de produto (CPU vs GPU)."""
    return True


__all__ = [
    "DTYPE_CPU",
    "DTYPE_GPU",
    "DTYPE_PROIBIDO",
    "DtypeProibido",
    "escolher_dispositivo",
    "dtype_para",
    "fluxo_unico",
    "validar_dtype",
]
