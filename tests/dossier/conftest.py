"""Fixtures de dossier: SQLite temporário e conversa com prova sintética."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from engine.armazenamento.repositorio import abrir


@pytest.fixture
def caminho_tmp(tmp_path: Path) -> Path:
    """Caminho de um SQLite temporário por teste."""
    pasta = tmp_path / "data"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / "lente.sqlite"


@pytest.fixture
def pasta_fontes(tmp_path: Path) -> Path:
    """Pasta com ficheiros fonte sintéticos."""
    pasta = tmp_path / "fontes"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _sha256_bytes(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def semear_conversa_com_prova(
    caminho_sqlite: Path,
    pasta_fontes: Path,
    *,
    bytes_fonte: bytes = b"As contas privilegiadas sao revistas anualmente.\n",
) -> dict[str, object]:
    """Cria documento, conversa, mensagens e citações de prova.

    Devolve ids e metadados úteis aos testes (caminho do ficheiro, SHA, etc.).
    """
    ficheiro = pasta_fontes / "politica-sintetica.txt"
    ficheiro.write_bytes(bytes_fonte)
    sha = _sha256_bytes(bytes_fonte)
    agora = "2026-03-12T14:00:00Z"
    caixas = [{"pagina": 1, "x": 72.0, "y": 410.0, "largura": 400.0, "altura": 24.0}]
    trecho = "As contas privilegiadas sao revistas anualmente."

    ligacao = abrir(caminho_sqlite)
    try:
        cur = ligacao.execute(
            """
            INSERT INTO documentos (
                caminho, titulo, tipo, sha256, estado,
                criado_em, actualizado_em
            ) VALUES (?, ?, 'texto', ?, 'ok', ?, ?)
            """,
            (str(ficheiro), "Política sintética", sha, agora, agora),
        )
        documento_id = int(cur.lastrowid)

        ligacao.execute(
            """
            INSERT INTO documento_hashes (
                documento_id, sha256, visto_em, activa
            ) VALUES (?, ?, ?, 1)
            """,
            (documento_id, sha, agora),
        )

        ligacao.execute(
            """
            INSERT INTO conversas (titulo, criado_em, actualizado_em)
            VALUES (?, ?, ?)
            """,
            ("Conversa de prova", agora, agora),
        )
        conversa_id = int(ligacao.execute("SELECT last_insert_rowid()").fetchone()[0])

        ligacao.execute(
            """
            INSERT INTO mensagens (
                conversa_id, papel, modo, lente, conteudo, criado_em
            ) VALUES (?, 'utilizador', 'procurar', 'verificar', ?, ?)
            """,
            (conversa_id, "Há revisão anual das contas privilegiadas?", agora),
        )

        frase_resposta = (
            "Sim: a revisão das contas privilegiadas está prevista anualmente. [1]"
        )
        ligacao.execute(
            """
            INSERT INTO mensagens (
                conversa_id, papel, modo, lente, conteudo, criado_em
            ) VALUES (?, 'assistente', 'procurar', 'verificar', ?, ?)
            """,
            (conversa_id, frase_resposta, agora),
        )
        mensagem_id = int(ligacao.execute("SELECT last_insert_rowid()").fetchone()[0])

        ligacao.execute(
            """
            INSERT INTO citacoes (
                mensagem_id, documento_id, indice, trecho_literal, ficheiro,
                pagina, offset_inicio, offset_fim, caixas_json, pontuacao_juiz,
                sha256_ficheiro
            ) VALUES (?, ?, 1, ?, ?, 1, 0, ?, ?, 0.91, ?)
            """,
            (
                mensagem_id,
                documento_id,
                trecho,
                str(ficheiro),
                len(trecho),
                json.dumps(caixas),
                sha,
            ),
        )

        for papel, modelo_id, revisao, lora_id in (
            ("embedding", "google/embeddinggemma-2-270m", "matryoshka-256", None),
            (
                "juiz",
                "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
                "onnx-int8",
                "lora-r8-local",
            ),
            ("e2b", "gemma-4-e2b-qat-q4", "1", None),
        ):
            ligacao.execute(
                """
                INSERT INTO versoes_modelo (
                    papel, modelo_id, revisao, lora_id, activo, registado_em
                ) VALUES (?, ?, ?, ?, 1, ?)
                """,
                (papel, modelo_id, revisao, lora_id, agora),
            )

        ligacao.commit()
    finally:
        ligacao.close()

    return {
        "conversa_id": conversa_id,
        "documento_id": documento_id,
        "mensagem_assistente_id": mensagem_id,
        "ficheiro": str(ficheiro),
        "sha256": sha,
        "trecho": trecho,
        "caixas": caixas,
        "frase_resposta": frase_resposta,
        "pergunta": "Há revisão anual das contas privilegiadas?",
    }
