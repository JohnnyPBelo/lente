"""Regressão de export Markdown + JSON do dossier."""

from __future__ import annotations

import json
from pathlib import Path

from engine.armazenamento.repositorio import abrir
from tests.dossier.conftest import semear_conversa_com_prova
from tests.regressao import apoio


def test_reg_dos_008(caminho_tmp: Path, pasta_fontes: Path) -> None:
    """Export produz Markdown legível e JSON aceite pelo esquema."""
    from engine.dossier.exportar import exportar_dossier
    from engine.dossier.fechar import fechar_dossier

    semente = semear_conversa_com_prova(caminho_tmp, pasta_fontes)
    ligacao = abrir(caminho_tmp)
    try:
        fechado = fechar_dossier(ligacao, int(semente["conversa_id"]))
        ligacao.commit()
        markdown, arquivo = exportar_dossier(ligacao, fechado["id"])
    finally:
        ligacao.close()

    assert isinstance(markdown, str)
    assert str(semente["pergunta"]) in markdown
    assert str(semente["trecho"]) in markdown
    assert str(semente["ficheiro"]) in markdown or "politica-sintetica" in markdown
    assert "página" in markdown.lower() or "pagina" in markdown.lower() or "p. " in markdown.lower() or "pág" in markdown.lower() or "1" in markdown

    assert isinstance(arquivo, dict)
    esquema = json.loads(
        (apoio.raiz() / "docs" / "dados" / "dossier.schema.json").read_text(
            encoding="utf-8"
        )
    )
    apoio.validar_instancia(arquivo, esquema, "export.json")
    assert arquivo["perguntas"][0]["texto"] == semente["pergunta"]
    assert arquivo["frases_aceites"][0]["trecho_literal"] == semente["trecho"]
    assert arquivo["ficheiros"][0]["sha256"] == semente["sha256"]
