"""Regressão REG-ALE-002: máximo de dez alertas."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.alertas.criar import criar_alerta
from engine.alertas.limite import MAX_ALERTAS, LimiteAlertas
from tests.alertas.apoio import ligacao_migrada


def test_reg_ale_002(caminho_tmp: Path) -> None:
    """Com dez alertas, o décimo primeiro falha com LimiteAlertas / limite_alertas."""
    assert MAX_ALERTAS == 10
    with ligacao_migrada(caminho_tmp) as ligacao:
        for i in range(MAX_ALERTAS):
            criar_alerta(ligacao, f"Vigiar tema {i}", lente="investigar")
        ligacao.commit()

        with pytest.raises(LimiteAlertas) as excinfo:
            criar_alerta(ligacao, "Um a mais", lente="investigar")

        erro = excinfo.value
        assert erro.codigo == "limite_alertas"
        assert "dez" in erro.mensagem.casefold()

        total = ligacao.execute("SELECT COUNT(*) AS n FROM alertas").fetchone()["n"]
        assert total == MAX_ALERTAS
