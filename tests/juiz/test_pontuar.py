"""Regressão REG-JUI-002: pontuação ONNX sem prosa e sem PyTorch."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

from engine.juiz.caminhos import MODELO_ID
from engine.juiz.pontuar import pontuar


class _SessaoDupla:
    """Double da sessão ONNX: overlap léxico; sem pesos nem download."""

    modelo_id = MODELO_ID
    ficheiro_onnx = "model_qint8_avx512_vnni.onnx"
    runtime = "onnx"
    quantizacao = "int8"

    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]:
        palavras_p = set(pergunta.casefold().split())
        scores: list[float] = []
        for frase in frases:
            palavras_f = set(frase.casefold().split())
            scores.append(float(len(palavras_p & palavras_f)))
        return scores


def test_reg_jui_002() -> None:
    """Par alinhado em PT pontua mais; só scores; caminho quente sem torch."""
    assert "torch" not in sys.modules

    pergunta = "Qual é a capital de Portugal?"
    alinhada = "Lisboa é a capital de Portugal."
    alheia = "O motor a vapor foi aperfeiçoado no século XIX."

    sessao = _SessaoDupla()
    scores = pontuar(pergunta, [alinhada, alheia], sessao=sessao)

    assert isinstance(scores, list)
    assert len(scores) == 2
    assert all(isinstance(s, float) for s in scores)
    assert scores[0] > scores[1]

    import importlib

    mod_pontuar = importlib.import_module("engine.juiz.pontuar")
    fonte = Path(mod_pontuar.__file__).read_text(encoding="utf-8")
    assert "import torch" not in fonte
    assert "from torch" not in fonte
    assert "pytorch" not in fonte.casefold()
    assert "torch" not in sys.modules
