"""Regressão REG-MOD-005: GPU acelera o mesmo código; sem segundo modo."""

from __future__ import annotations

import inspect
import math

from engine.embeddings import carregar as carregar_mod
from engine.embeddings.carregar import embutir
from engine.embeddings.dispositivo import (
    DTYPE_CPU,
    DTYPE_GPU,
    DTYPE_PROIBIDO,
    dtype_para,
    escolher_dispositivo,
    fluxo_unico,
)
from tests.embeddings import apoio


def test_reg_mod_005() -> None:
    """CPU e GPU partilham o mesmo fluxo de embutir; GPU só muda dispositivo/dtype."""
    assert fluxo_unico() is True
    assert escolher_dispositivo(tem_gpu=False) == "cpu"
    assert escolher_dispositivo(tem_gpu=True) == "cuda"
    assert dtype_para("cpu") == DTYPE_CPU
    assert dtype_para("cuda") == DTYPE_GPU

    frase = "O mesmo codigo de embedding corre com ou sem GPU."
    sessao_cpu = apoio.sessao_dupla(dispositivo="cpu", dtype=DTYPE_CPU)
    sessao_gpu = apoio.sessao_dupla(dispositivo="cuda", dtype=DTYPE_GPU)

    v_cpu = embutir(frase, sessao=sessao_cpu)
    v_gpu = embutir(frase, sessao=sessao_gpu)
    assert len(v_cpu) == len(v_gpu) == 256
    # Mesmo double → mesmos valores; o dtype de sessão difere, o código não.
    assert v_cpu == v_gpu
    assert math.isclose(math.sqrt(sum(x * x for x in v_cpu)), 1.0, rel_tol=1e-5)

    fonte = inspect.getsource(carregar_mod.embutir)
    assert "modo_gpu" not in fonte.casefold()
    assert "modo_cpu" not in fonte.casefold()
    # O caminho activo nunca escolhe float16 (só o rejeita).
    assert 'dtype="float16"' not in fonte
    assert "torch.float16" not in fonte
    assert DTYPE_PROIBIDO not in (
        sessao_cpu.dtype,
        sessao_gpu.dtype,
    )
