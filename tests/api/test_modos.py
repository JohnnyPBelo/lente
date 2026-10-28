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


def test_confrontar_texto_colado_sem_injectaveis_nao_fica_tudo_zero() -> None:
    """Sem _cos/_j_*: Jaccard lexical deve pontuar sobreposição (issue #76)."""
    r = confrontar(
        {
            "chat_id": "cht_01",
            "trecho_a": {
                "texto": "O impacto ambiental no rio Douro é moderado."
            },
            "trecho_b": {
                "texto": "O impacto ambiental no rio Douro requer mitigação."
            },
        }
    )
    assert r["cos"] > 0.0
    assert r["j_ab"] > 0.0
    assert r["j_ba"] > 0.0
    assert r["score"] > 0.0


def test_confrontar_usa_pontuar_e_cosseno_injectados() -> None:
    """Com doubles de juiz/embedding, os scores não caem a zero (issue #76)."""

    def pontuar(a: str, b: str) -> float:
        del a, b
        return 0.71

    def cosseno(a: str, b: str) -> float:
        del a, b
        return 0.82

    r = confrontar(
        {
            "chat_id": "cht_01",
            "trecho_a": {"texto": "impacto moderado nos peixes"},
            "trecho_b": {"texto": "mitigação do impacto nos peixes"},
        },
        pontuar=pontuar,
        cosseno=cosseno,
    )
    assert r["cos"] == pytest.approx(0.82)
    assert r["j_ab"] == pytest.approx(0.71)
    assert r["j_ba"] == pytest.approx(0.71)
    assert r["leitura"] == "concordam"
    assert r["score"] == pytest.approx(0.71)


def test_correlacionar_sem_indice_nao_inventa_docs() -> None:
    """Sem pesquisar injectado → eventos vazios (issue #51)."""
    r = correlacionar(
        {
            "chat_id": "cht_01",
            "conceito_a": "acessos",
            "conceito_b": "auditoria",
            "lente": "investigar",
        }
    )
    assert r["papeis"] == ["A", "B", "relacao"]
    assert r["eventos"] == []


def test_correlacionar_papeis_a_b_relacao() -> None:
    def pesquisar(conceito: str, papel: str):
        return [
            {
                "tipo": "excerto",
                "papel": papel,
                "documento_id": f"doc_{len(conceito)}",
                "pagina": 1,
                "texto": conceito,
                "offsets": {"inicio": 0, "fim": len(conceito)},
                "caixas": [],
                "score_juiz": 0.7,
            }
        ]

    r = correlacionar(
        {
            "chat_id": "cht_01",
            "conceito_a": "acessos",
            "conceito_b": "auditoria",
            "lente": "investigar",
        },
        pesquisar=pesquisar,
    )
    assert r["papeis"] == ["A", "B", "relacao"]
    papeis = {e["papel"] for e in r["eventos"]}
    assert papeis == {"A", "B", "relacao"}
    assert all(str(e["documento_id"]).startswith("doc_") for e in r["eventos"])


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
