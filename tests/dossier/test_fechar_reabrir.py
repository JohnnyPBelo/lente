"""Regressões de fecho e reabertura do dossier de prova."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.armazenamento.repositorio import abrir
from tests.dossier.conftest import semear_conversa_com_prova


def _contar_dossiers(caminho: Path) -> int:
    ligacao = abrir(caminho)
    try:
        return int(ligacao.execute("SELECT COUNT(*) FROM dossiers").fetchone()[0])
    finally:
        ligacao.close()


def _adicionar_mensagem(caminho: Path, conversa_id: int, texto: str) -> None:
    ligacao = abrir(caminho)
    try:
        ligacao.execute(
            """
            INSERT INTO mensagens (
                conversa_id, papel, modo, lente, conteudo, criado_em
            ) VALUES (?, 'utilizador', 'procurar', 'verificar', ?, ?)
            """,
            (conversa_id, texto, "2026-03-12T15:00:00Z"),
        )
        ligacao.commit()
    finally:
        ligacao.close()


def test_reg_dos_003(caminho_tmp: Path, pasta_fontes: Path) -> None:
    """Fechar é botão explícito: mensagens sozinhas não gravam fotografia."""
    from engine.dossier.fechar import fechar_dossier

    semente = semear_conversa_com_prova(caminho_tmp, pasta_fontes)
    conversa_id = int(semente["conversa_id"])

    assert _contar_dossiers(caminho_tmp) == 0

    _adicionar_mensagem(caminho_tmp, conversa_id, "Segunda pergunta sem fechar.")
    assert _contar_dossiers(caminho_tmp) == 0

    ligacao = abrir(caminho_tmp)
    try:
        resultado = fechar_dossier(ligacao, conversa_id)
        ligacao.commit()
    finally:
        ligacao.close()

    assert resultado["id"]
    assert _contar_dossiers(caminho_tmp) == 1


def test_reg_dos_004(
    caminho_tmp: Path, pasta_fontes: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fotografia tem prova completa; reabrir não chama embedding, juiz nem E2B."""
    from engine.dossier.fechar import fechar_dossier
    from engine.dossier.reabrir import reabrir_dossier

    semente = semear_conversa_com_prova(caminho_tmp, pasta_fontes)
    conversa_id = int(semente["conversa_id"])

    chamadas: list[str] = []

    def _proibir_embedding(*_a, **_k):
        chamadas.append("embedding")
        raise AssertionError("reabrir não pode chamar EmbeddingGemma")

    def _proibir_juiz(*_a, **_k):
        chamadas.append("juiz")
        raise AssertionError("reabrir não pode chamar o juiz")

    def _proibir_e2b(*_a, **_k):
        chamadas.append("e2b")
        raise AssertionError("reabrir não pode chamar o E2B")

    monkeypatch.setattr(
        "engine.embeddings.carregar.carregar_modelo",
        _proibir_embedding,
        raising=False,
    )
    monkeypatch.setattr("engine.juiz.pontuar.pontuar", _proibir_juiz, raising=False)
    monkeypatch.setattr(
        "engine.juiz.carregar.carregar_sessao", _proibir_juiz, raising=False
    )

    ligacao = abrir(caminho_tmp)
    try:
        fechado = fechar_dossier(ligacao, conversa_id)
        ligacao.commit()
        dossier_id = fechado["id"]

        linha = ligacao.execute(
            "SELECT perguntas_json, frases_json FROM dossiers WHERE id = ?",
            (int(str(dossier_id).removeprefix("dos_")),)
            if str(dossier_id).startswith("dos_")
            else (dossier_id,),
        ).fetchone()
        assert linha is not None
        perguntas = json.loads(linha[0])
        frases = json.loads(linha[1])
        assert perguntas
        assert perguntas[0]["texto"] == semente["pergunta"]
        assert frases
        frase = frases[0]
        assert frase["trecho_literal"] == semente["trecho"]
        assert frase["ficheiro"] == semente["ficheiro"]
        assert frase["pagina"] == 1
        assert frase["offset_inicio"] == 0
        assert frase["offset_fim"] == len(str(semente["trecho"]))
        assert frase["caixas"] == semente["caixas"]
        assert frase["pontuacao_juiz"] == pytest.approx(0.91)

        # Simula ausência de pesos/mocks depois do fecho.
        monkeypatch.setattr(
            "engine.embeddings.indexar.indexar_documento",
            _proibir_embedding,
            raising=False,
        )
        try:
            import engine.resposta  # noqa: F401
        except ImportError:
            pass
        else:
            monkeypatch.setattr(
                "engine.resposta.gerar", _proibir_e2b, raising=False
            )

        vista = reabrir_dossier(ligacao, dossier_id)
    finally:
        ligacao.close()

    assert chamadas == []
    assert vista["fonte_alterada"] is False
    frases_vista = vista.get("frases_aceites") or vista.get("frases")
    assert frases_vista
    assert frases_vista[0]["trecho_literal"] == semente["trecho"] or frases_vista[0].get(
        "trecho"
    ) == semente["trecho"]
    assert frases_vista[0]["pagina"] == 1
    assert frases_vista[0]["offset_inicio"] == 0
    assert frases_vista[0]["offset_fim"] == len(str(semente["trecho"]))


def test_reg_dos_005(caminho_tmp: Path, pasta_fontes: Path) -> None:
    """Cada fonte citada guarda o SHA-256 dos bytes no fecho."""
    from engine.dossier.fechar import fechar_dossier

    semente = semear_conversa_com_prova(caminho_tmp, pasta_fontes)
    ligacao = abrir(caminho_tmp)
    try:
        fechado = fechar_dossier(ligacao, int(semente["conversa_id"]))
        ligacao.commit()
        dossier_id = fechado["id"]
        row_id = (
            int(str(dossier_id).removeprefix("dos_"))
            if str(dossier_id).startswith("dos_")
            else int(dossier_id)
        )
        ficheiros = json.loads(
            ligacao.execute(
                "SELECT ficheiros_json FROM dossiers WHERE id = ?", (row_id,)
            ).fetchone()[0]
        )
        frases = json.loads(
            ligacao.execute(
                "SELECT frases_json FROM dossiers WHERE id = ?", (row_id,)
            ).fetchone()[0]
        )
    finally:
        ligacao.close()

    assert ficheiros
    assert ficheiros[0]["caminho"] == semente["ficheiro"]
    assert ficheiros[0]["sha256"] == semente["sha256"]
    assert frases[0]["sha256_ficheiro"] == semente["sha256"]


def test_reg_dos_006(caminho_tmp: Path, pasta_fontes: Path) -> None:
    """Fotografia inclui data e versões EmbeddingGemma, juiz(+LoRA) e E2B."""
    from engine.dossier.fechar import fechar_dossier

    semente = semear_conversa_com_prova(caminho_tmp, pasta_fontes)
    ligacao = abrir(caminho_tmp)
    try:
        fechado = fechar_dossier(ligacao, int(semente["conversa_id"]))
        ligacao.commit()
        assert "fechado_em" in fechado
        assert fechado["fechado_em"]

        dossier_id = fechado["id"]
        row_id = (
            int(str(dossier_id).removeprefix("dos_"))
            if str(dossier_id).startswith("dos_")
            else int(dossier_id)
        )
        linha = ligacao.execute(
            """
            SELECT fechado_em, versao_embedding, versao_juiz, versao_e2b
            FROM dossiers WHERE id = ?
            """,
            (row_id,),
        ).fetchone()
    finally:
        ligacao.close()

    assert linha is not None
    fechado_em, emb, juiz, e2b = linha
    assert fechado_em
    assert "embeddinggemma" in emb.lower() or "google/embeddinggemma" in emb
    assert "mmarco" in juiz.lower() or "juiz" in juiz.lower()
    assert "lora" in juiz.lower()
    assert "e2b" in e2b.lower() or "gemma" in e2b.lower()


def test_reg_dos_007(caminho_tmp: Path, pasta_fontes: Path) -> None:
    """Hash diferente → fonte_alterada; prova antiga intacta; sem reindexação."""
    from engine.dossier.fechar import fechar_dossier
    from engine.dossier.reabrir import reabrir_dossier

    semente = semear_conversa_com_prova(caminho_tmp, pasta_fontes)
    ficheiro = Path(str(semente["ficheiro"]))
    sha_fecho = str(semente["sha256"])
    trecho = str(semente["trecho"])

    ligacao = abrir(caminho_tmp)
    try:
        fechado = fechar_dossier(ligacao, int(semente["conversa_id"]))
        ligacao.commit()
        dossier_id = fechado["id"]

        intacta = reabrir_dossier(ligacao, dossier_id)
        assert intacta["fonte_alterada"] is False

        ficheiro.write_bytes(b"conteudo alterado depois do fecho\n")
        alterada = reabrir_dossier(ligacao, dossier_id)
    finally:
        ligacao.close()

    assert alterada["fonte_alterada"] is True
    frases = alterada.get("frases_aceites") or alterada.get("frases")
    assert frases
    trecho_lido = frases[0].get("trecho_literal") or frases[0].get("trecho")
    assert trecho_lido == trecho
    assert frases[0]["pontuacao_juiz"] == pytest.approx(0.91) or frases[0].get(
        "score_juiz"
    ) == pytest.approx(0.91)
    sha_frase = frases[0].get("sha256_ficheiro") or frases[0].get("hash_sha256_fecho")
    assert sha_frase == sha_fecho

    # Sem reindexação automática: o documento na BD mantém o SHA antigo
    # até acção explícita (fora do âmbito deste plano).
    ligacao = abrir(caminho_tmp)
    try:
        sha_bd = ligacao.execute(
            "SELECT sha256 FROM documentos WHERE id = ?",
            (semente["documento_id"],),
        ).fetchone()[0]
    finally:
        ligacao.close()
    assert sha_bd == sha_fecho


def test_citacao_dossier_abre_na_pagina(caminho_tmp: Path, pasta_fontes: Path) -> None:
    """Citação no dossier expõe página e caixas para o leitor (prova gravada)."""
    from engine.dossier.fechar import fechar_dossier
    from engine.dossier.reabrir import reabrir_dossier

    semente = semear_conversa_com_prova(caminho_tmp, pasta_fontes)
    ligacao = abrir(caminho_tmp)
    try:
        fechado = fechar_dossier(ligacao, int(semente["conversa_id"]))
        ligacao.commit()
        vista = reabrir_dossier(ligacao, fechado["id"])
    finally:
        ligacao.close()

    frases = vista.get("frases_aceites") or vista.get("frases")
    assert frases
    assert frases[0]["pagina"] == 1
    caixas = frases[0].get("caixas")
    assert caixas
    assert caixas[0]["pagina"] == 1
