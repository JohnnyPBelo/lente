"""Fechar dossier sob pedido: grava fotografia imutável no SQLite."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from engine.ingestao.hash import sha256_ficheiro
from engine.ingestao.tipos import FicheiroInexistente


def _agora_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _id_publico(dossier_id: int) -> str:
    return f"dos_{dossier_id}"


def _versoes_activas(ligacao: sqlite3.Connection) -> dict[str, str]:
    """Lê versões activas; juiz inclui LoRA se existir."""
    resultado = {"embedding": "desconhecido", "juiz": "desconhecido", "e2b": "desconhecido"}
    linhas = ligacao.execute(
        """
        SELECT papel, modelo_id, revisao, lora_id
        FROM versoes_modelo
        WHERE activo = 1
        """
    ).fetchall()
    for papel, modelo_id, revisao, lora_id in linhas:
        if papel == "embedding":
            resultado["embedding"] = f"{modelo_id}@{revisao}"
        elif papel == "juiz":
            base = f"{modelo_id}+{revisao}"
            if lora_id:
                base = f"{base}+{lora_id}"
            resultado["juiz"] = base
        elif papel == "e2b":
            resultado["e2b"] = f"{modelo_id}@{revisao}" if revisao else str(modelo_id)
    return resultado


def _sha_fecho(caminho: str, sha_citacao: str | None) -> str:
    """SHA do ficheiro em disco; cai no digest gravado se o caminho falhar."""
    if caminho and caminho.strip():
        try:
            return sha256_ficheiro(caminho)
        except FicheiroInexistente:
            pass
    if sha_citacao:
        return sha_citacao
    raise FicheiroInexistente(caminho or ".")


def _perguntas_do_ecra(ligacao: sqlite3.Connection, conversa_id: int) -> list[dict[str, Any]]:
    linhas = ligacao.execute(
        """
        SELECT conteudo, modo, lente
        FROM mensagens
        WHERE conversa_id = ? AND papel = 'utilizador'
        ORDER BY id
        """,
        (conversa_id,),
    ).fetchall()
    perguntas: list[dict[str, Any]] = []
    for conteudo, modo, lente in linhas:
        item: dict[str, Any] = {"texto": conteudo}
        if modo:
            item["modo"] = modo
        if lente:
            item["lente"] = lente
        perguntas.append(item)
    return perguntas


def _frases_aceites(
    ligacao: sqlite3.Connection, conversa_id: int
) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    """Frases que passaram as duas portas (citações) + ficheiros citados."""
    linhas = ligacao.execute(
        """
        SELECT
            c.indice,
            m.conteudo,
            c.trecho_literal,
            c.ficheiro,
            d.caminho,
            c.pagina,
            c.offset_inicio,
            c.offset_fim,
            c.caixas_json,
            c.pontuacao_juiz,
            c.sha256_ficheiro,
            d.sha256,
            d.titulo
        FROM citacoes c
        JOIN mensagens m ON m.id = c.mensagem_id
        JOIN documentos d ON d.id = c.documento_id
        WHERE m.conversa_id = ?
        ORDER BY m.id, c.indice
        """,
        (conversa_id,),
    ).fetchall()

    frases: list[dict[str, Any]] = []
    ficheiros: dict[str, dict[str, str]] = {}
    for (
        indice,
        conteudo,
        trecho,
        ficheiro_cit,
        caminho_doc,
        pagina,
        offset_inicio,
        offset_fim,
        caixas_json,
        pontuacao,
        sha_citacao,
        sha_doc,
        titulo,
    ) in linhas:
        ficheiro = (ficheiro_cit or "").strip() or str(caminho_doc or "")
        sha_gravado = sha_citacao or sha_doc
        sha = _sha_fecho(ficheiro, sha_gravado)
        caixas = json.loads(caixas_json) if caixas_json else []
        frases.append(
            {
                "indice": int(indice),
                "frase_resposta": conteudo,
                "trecho_literal": trecho,
                "ficheiro": ficheiro,
                "pagina": int(pagina) if pagina is not None else 1,
                "offset_inicio": int(offset_inicio or 0),
                "offset_fim": int(offset_fim or 0),
                "caixas": caixas,
                "pontuacao_juiz": float(pontuacao) if pontuacao is not None else 0.0,
                "sha256_ficheiro": sha,
            }
        )
        if ficheiro not in ficheiros:
            entrada: dict[str, str] = {"caminho": ficheiro, "sha256": sha}
            if titulo:
                entrada["titulo"] = titulo
            ficheiros[ficheiro] = entrada
    return frases, ficheiros


def _montar_export_json(
    *,
    dossier_id: int,
    conversa_id: int,
    titulo: str,
    fechado_em: str,
    perguntas: list[dict[str, Any]],
    frases: list[dict[str, Any]],
    ficheiros: list[dict[str, str]],
    versoes: dict[str, str],
) -> dict[str, Any]:
    return {
        "format_version": "1",
        "id": _id_publico(dossier_id),
        "titulo": titulo,
        "conversa_id": conversa_id,
        "fechado_em": fechado_em,
        "perguntas": perguntas,
        "frases_aceites": frases,
        "ficheiros": ficheiros,
        "versoes_modelo": {
            "embedding": versoes["embedding"],
            "juiz": versoes["juiz"],
            "e2b": versoes["e2b"],
        },
    }


def fechar_dossier(
    ligacao: sqlite3.Connection,
    conversa_id: int,
    *,
    titulo: str | None = None,
    versoes: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Grava a fotografia do chat actual. Só corre sob pedido explícito.

    Não é chamado automaticamente ao acrescentar mensagens.
    """
    row = ligacao.execute(
        "SELECT titulo FROM conversas WHERE id = ? AND apagada = 0",
        (conversa_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"Conversa inexistente: {conversa_id}")

    titulo_final = titulo or row[0] or "Dossier"
    perguntas = _perguntas_do_ecra(ligacao, conversa_id)
    if not perguntas:
        raise ValueError("Não há perguntas no ecrã para fechar o dossier.")

    frases, ficheiros_map = _frases_aceites(ligacao, conversa_id)
    ficheiros = list(ficheiros_map.values())
    if not ficheiros:
        # Esquema exige minItems 1; sem citações não há prova fechável.
        raise ValueError("Não há frases aceites (prova) para fechar o dossier.")

    versoes_finais = versoes or _versoes_activas(ligacao)
    fechado_em = _agora_utc()

    cur = ligacao.execute(
        """
        INSERT INTO dossiers (
            conversa_id, titulo, fechado_em,
            perguntas_json, frases_json, ficheiros_json,
            versao_embedding, versao_juiz, versao_e2b, export_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """,
        (
            conversa_id,
            titulo_final,
            fechado_em,
            json.dumps(perguntas, ensure_ascii=False),
            json.dumps(frases, ensure_ascii=False),
            json.dumps(ficheiros, ensure_ascii=False),
            versoes_finais["embedding"],
            versoes_finais["juiz"],
            versoes_finais["e2b"],
        ),
    )
    dossier_id = int(cur.lastrowid)

    export = _montar_export_json(
        dossier_id=dossier_id,
        conversa_id=conversa_id,
        titulo=titulo_final,
        fechado_em=fechado_em,
        perguntas=perguntas,
        frases=frases,
        ficheiros=ficheiros,
        versoes=versoes_finais,
    )
    ligacao.execute(
        "UPDATE dossiers SET export_json = ? WHERE id = ?",
        (json.dumps(export, ensure_ascii=False), dossier_id),
    )

    juiz_lora = None
    juiz = versoes_finais["juiz"]
    if "+lora" in juiz.lower() or "lora-" in juiz.lower():
        # Extrai o sufixo LoRA se estiver no identificador composto.
        partes = juiz.split("+")
        for parte in partes:
            if "lora" in parte.lower():
                juiz_lora = parte
                break

    return {
        "id": _id_publico(dossier_id),
        "fechado_em": fechado_em,
        "versoes": {
            "embedding": versoes_finais["embedding"],
            "juiz": versoes_finais["juiz"],
            "juiz_lora": juiz_lora,
            "escritor": versoes_finais["e2b"],
        },
    }


def resolver_id(dossier_id: int | str) -> int:
    """Aceita ``dos_N`` ou inteiro."""
    if isinstance(dossier_id, int):
        return dossier_id
    texto = str(dossier_id)
    if texto.startswith("dos_"):
        return int(texto.removeprefix("dos_"))
    return int(texto)
