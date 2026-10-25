"""Regressão REG-MIG-001: migração inicial e integridade do esquema."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from engine.armazenamento.ligacao import abrir_ligacao
from engine.armazenamento.migracoes import aplicar_migracoes


TABELAS_NUCLEO = ("documentos", "documento_hashes", "blocos", "frases")


def _tabelas(ligacao: sqlite3.Connection) -> set[str]:
    linhas = ligacao.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()
    return {linha[0] for linha in linhas}


def test_reg_mig_001(caminho_tmp: Path) -> None:
    """Após aplicar migrações: user_version, tabelas, idempotência, FK e CHECK."""
    aplicar_migracoes(caminho_tmp)

    with abrir_ligacao(caminho_tmp) as ligacao:
        versao = ligacao.execute("PRAGMA user_version").fetchone()[0]
        assert versao >= 1
        presentes = _tabelas(ligacao)
        for tabela in TABELAS_NUCLEO:
            assert tabela in presentes, f"Falta a tabela {tabela}"

    # Segunda chamada: no-op (não falha nem recria tabelas).
    aplicar_migracoes(caminho_tmp)
    with abrir_ligacao(caminho_tmp) as ligacao:
        assert ligacao.execute("PRAGMA user_version").fetchone()[0] >= 1
        for tabela in TABELAS_NUCLEO:
            assert tabela in _tabelas(ligacao)

    with abrir_ligacao(caminho_tmp) as ligacao:
        # FK: bloco com documento inexistente tem de falhar.
        with pytest.raises(sqlite3.IntegrityError):
            ligacao.execute(
                "INSERT INTO blocos ("
                "documento_id, hash_id, ordem, texto, "
                "offset_inicio, offset_fim, tokens_aprox"
                ") VALUES (999, 999, 0, 'x', 0, 1, 1)"
            )
        ligacao.rollback()

        # CHECK de estado em documentos.
        for estado_invalido in ("", "pronto", "OK", "indexado"):
            with pytest.raises(sqlite3.IntegrityError):
                ligacao.execute(
                    "INSERT INTO documentos ("
                    "caminho, titulo, tipo, sha256, estado, criado_em, actualizado_em"
                    ") VALUES (?, 't', 'txt', 'abc', ?, '2026-01-01T00:00:00Z',"
                    " '2026-01-01T00:00:00Z')",
                    (f"/tmp/invalido-{estado_invalido or 'vazio'}", estado_invalido),
                )
            ligacao.rollback()

        for estado_ok in ("ok", "desactualizado", "a_indexar", "erro"):
            ligacao.execute(
                "INSERT INTO documentos ("
                "caminho, titulo, tipo, sha256, estado, criado_em, actualizado_em"
                ") VALUES (?, 't', 'txt', 'abc', ?, '2026-01-01T00:00:00Z',"
                " '2026-01-01T00:00:00Z')",
                (f"/tmp/ok-{estado_ok}", estado_ok),
            )
        ligacao.commit()
