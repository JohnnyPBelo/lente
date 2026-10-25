"""Juiz ONNX int8: decisão rápida sem prosa (highlight / portas)."""

from __future__ import annotations

from engine.juiz.caminhos import (
    FICHEIRO_ARM64,
    FICHEIRO_AVX512,
    MODELO_ID,
    IdentidadeJuiz,
    caminho_onnx,
    ficheiro_onnx_maquina,
    identificar_modelo,
    pasta_juiz,
)
from engine.juiz.carregar import (
    DecisorRecusado,
    PesosJuizAusentes,
    SessaoJuiz,
    carregar_sessao,
    identificador_aceite,
    registar_versao,
    validar_modelo_id,
)
from engine.juiz.pontuar import pontuar

__all__ = [
    "FICHEIRO_ARM64",
    "FICHEIRO_AVX512",
    "MODELO_ID",
    "DecisorRecusado",
    "IdentidadeJuiz",
    "PesosJuizAusentes",
    "SessaoJuiz",
    "caminho_onnx",
    "carregar_sessao",
    "ficheiro_onnx_maquina",
    "identificador_aceite",
    "identificar_modelo",
    "pasta_juiz",
    "pontuar",
    "registar_versao",
    "validar_modelo_id",
]
