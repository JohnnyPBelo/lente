"""Export Markdown legível + JSON de arquivo (schema dossier)."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from engine.dossier.reabrir import fotografia_canonica


def _markdown_de_fotografia(foto: dict[str, Any]) -> str:
    linhas: list[str] = []
    titulo = foto.get("titulo") or "Dossier"
    linhas.append(f"# {titulo}")
    linhas.append("")
    if foto.get("fechado_em"):
        linhas.append(f"Fechado em: {foto['fechado_em']}")
        linhas.append("")

    linhas.append("## Perguntas")
    linhas.append("")
    for pergunta in foto.get("perguntas") or []:
        texto = pergunta.get("texto", "")
        meta = []
        if pergunta.get("modo"):
            meta.append(str(pergunta["modo"]))
        if pergunta.get("lente"):
            meta.append(str(pergunta["lente"]))
        sufixo = f" ({', '.join(meta)})" if meta else ""
        linhas.append(f"- {texto}{sufixo}")
    linhas.append("")

    linhas.append("## Frases citadas")
    linhas.append("")
    for frase in foto.get("frases_aceites") or []:
        indice = frase.get("indice", "")
        trecho = frase.get("trecho_literal", "")
        ficheiro = frase.get("ficheiro", "")
        pagina = frase.get("pagina", "")
        prosa = frase.get("frase_resposta")
        if prosa:
            linhas.append(f"### [{indice}] {prosa}")
        else:
            linhas.append(f"### [{indice}]")
        linhas.append("")
        linhas.append(f"> {trecho}")
        linhas.append("")
        linhas.append(f"- Ficheiro: `{ficheiro}`")
        linhas.append(f"- Página: {pagina}")
        if frase.get("pontuacao_juiz") is not None:
            linhas.append(f"- Pontuação do juiz: {frase['pontuacao_juiz']}")
        linhas.append("")

    linhas.append("## Ficheiros")
    linhas.append("")
    for ficheiro in foto.get("ficheiros") or []:
        caminho = ficheiro.get("caminho", "")
        sha = ficheiro.get("sha256", "")
        nome = ficheiro.get("titulo")
        rotulo = f"{nome} — " if nome else ""
        linhas.append(f"- {rotulo}`{caminho}` (SHA-256: `{sha}`)")
    linhas.append("")

    versoes = foto.get("versoes_modelo") or {}
    if versoes:
        linhas.append("## Versões dos modelos")
        linhas.append("")
        for chave in ("embedding", "juiz", "e2b"):
            if chave in versoes:
                linhas.append(f"- {chave}: `{versoes[chave]}`")
        linhas.append("")

    return "\n".join(linhas).rstrip() + "\n"


def exportar_dossier(
    ligacao: sqlite3.Connection, dossier_id: int | str
) -> tuple[str, dict[str, Any]]:
    """Devolve ``(markdown, json_arquivo)`` com os mesmos campos da fotografia."""
    foto = fotografia_canonica(ligacao, dossier_id)
    # Cópia rasa suficiente: a fotografia já é o molde do schema.
    arquivo = json.loads(json.dumps(foto))
    return _markdown_de_fotografia(foto), arquivo
