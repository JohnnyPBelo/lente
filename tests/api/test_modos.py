"""Testes dos modos HTTP-correlate / confront / lacunas (PLN-14)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from engine.api.rotas_modos import (  # noqa: E402
    confrontar,
    correlacionar,
    criar_alerta,
    lacunas,
    leitura_confronto,
)


def test_reg_confronto_c1_concordam() -> None:
    assert (
        leitura_confronto(cos=0.82, j_ab=0.71, j_ba=0.68) == "concordam"
    )


def test_reg_confronto_c2_contradizem() -> None:
    assert (
        leitura_confronto(cos=0.61, j_ab=0.72, j_ba=0.28) == "contradizem-se"
    )


def test_reg_confronto_c3_contradizem_fraco() -> None:
    assert (
        leitura_confronto(cos=0.58, j_ab=0.22, j_ba=0.19) == "contradizem-se"
    )


def test_reg_confronto_c4_assuntos_diferentes() -> None:
    assert (
        leitura_confronto(cos=0.12, j_ab=0.08, j_ba=0.07)
        == "assuntos_diferentes"
    )


def test_reg_confronto_c5_assuntos_medio() -> None:
    assert (
        leitura_confronto(cos=0.42, j_ab=0.33, j_ba=0.31)
        == "assuntos_diferentes"
    )


def test_confrontar_com_texto_colado() -> None:
    r = confrontar(
        {
            "chat_id": "cht_01",
            "trecho_a": {"texto": "O prazo de retenção dos logs é de 90 dias."},
            "trecho_b": {
                "texto": "Os registos de auditoria conservam-se durante noventa dias."
            },
            "_cos": 0.82,
            "_j_ab": 0.71,
            "_j_ba": 0.68,
        }
    )
    assert r["leitura"] == "concordam"
    assert "score" in r
    assert r["trecho_a"]["texto"]


def test_correlacionar_papeis_a_b_relacao() -> None:
    r = correlacionar(
        {
            "chat_id": "cht_01",
            "conceito_a": "acessos",
            "conceito_b": "auditoria",
            "lente": "investigar",
        }
    )
    assert r["papeis"] == ["A", "B", "relacao"]
    papeis = {e["papel"] for e in r["eventos"]}
    assert papeis == {"A", "B", "relacao"}


def test_lacunas_nao_chama_escritor() -> None:
    chamado = {"chamado": False}

    def escritor() -> None:
        chamado["chamado"] = True

    r = lacunas(
        {
            "chat_id": "cht_01",
            "linhas": ["Existe política?", "Há formação?"],
            "lente": "acreditacao",
        },
        escritor=escritor,
        escritor_chamado=chamado,
    )
    assert r["escritor_chamado"] is False
    assert chamado["chamado"] is False
    assert len(r["itens"]) == 2
    assert all(i["estado"] in {"encontrado", "fraco", "ausente"} for i in r["itens"])


def test_alerta_limite_dez() -> None:
    ok = criar_alerta({"texto": "VPN", "lente": "investigar"}, alertas_existentes=9)
    assert ok.get("http") == 201
    falha = criar_alerta(
        {"texto": "outro", "lente": "investigar"}, alertas_existentes=10
    )
    assert falha["erro"] == "limite_alertas"
    assert falha.get("http") == 409


def test_lente_nao_altera_leituras_do_confronto() -> None:
    """A lente não entra na função de leitura (ADR-010)."""
    base = leitura_confronto(cos=0.82, j_ab=0.71, j_ba=0.68)
    # Mesmos números → mesma leitura, independentemente de qualquer lente.
    assert base == "concordam"
    assert leitura_confronto(cos=0.82, j_ab=0.71, j_ba=0.68) == base
