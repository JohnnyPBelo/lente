"""Regressão REG-JUI-001: identidade do juiz ONNX int8 mmarco."""

from __future__ import annotations

import platform

import pytest

from engine.armazenamento.repositorio import abrir
from engine.juiz.caminhos import (
    FICHEIRO_ARM64,
    FICHEIRO_AVX512,
    MODELO_ID,
    ficheiro_onnx_maquina,
    identificar_modelo,
)
from engine.juiz.carregar import PesosJuizAusentes, carregar_sessao, registar_versao


def test_reg_jui_001() -> None:
    """O decisor é o ONNX int8 mmarco; ficheiro avx512 ou arm64; nunca Jev/Qwen/DeBERTa."""
    info = identificar_modelo()

    assert info.modelo_id == MODELO_ID
    assert info.modelo_id == "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
    assert info.runtime == "onnx"
    assert info.quantizacao == "int8"
    assert info.ficheiro_onnx == ficheiro_onnx_maquina()

    maquina = platform.machine().lower()
    if maquina in {"arm64", "aarch64"}:
        assert info.ficheiro_onnx == FICHEIRO_ARM64
    else:
        assert info.ficheiro_onnx == FICHEIRO_AVX512

    texto = f"{info.modelo_id} {info.ficheiro_onnx} {info.runtime}".casefold()
    assert "jev" not in texto
    assert "qwen" not in texto
    assert "deberta" not in texto


def test_pesos_ausentes_erro_tipado_com_caminho_manual(tmp_path) -> None:
    """Sem pesos locais: erro tipado com caminho manual; sem descarregar."""
    pasta = tmp_path / "models" / "juiz"
    pasta.mkdir(parents=True)

    with pytest.raises(PesosJuizAusentes) as excinfo:
        carregar_sessao(raiz_modelos=tmp_path / "models")

    erro = excinfo.value
    assert erro.caminho_manual
    assert "juiz" in erro.caminho_manual
    assert erro.caminho_manual.endswith(ficheiro_onnx_maquina()) or ficheiro_onnx_maquina() in erro.caminho_manual


def test_regista_versao_em_versoes_modelo(caminho_tmp) -> None:
    """Carga bem-sucedida (ou registo explícito) grava o juiz em versoes_modelo."""
    ligacao = abrir(caminho_tmp)
    revisao = "onnx-int8-teste"
    registar_versao(
        ligacao,
        revisao=revisao,
        ficheiro_onnx=ficheiro_onnx_maquina(),
    )
    linha = ligacao.execute(
        "SELECT papel, modelo_id, revisao, lora_id, activo FROM versoes_modelo "
        "WHERE papel = 'juiz' AND activo = 1"
    ).fetchone()
    assert linha is not None
    assert linha[0] == "juiz"
    assert linha[1] == MODELO_ID
    assert linha[2] == revisao
    assert linha[3] is None
    assert linha[4] == 1
