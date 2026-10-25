"""Regressão REG-DIA-001 e REG-DIA-002: diário local só de acrescentar."""

from __future__ import annotations

import ast
import inspect
import sqlite3
from pathlib import Path

import pytest

from engine.armazenamento.ligacao import abrir_ligacao
from engine.armazenamento.migracoes import aplicar_migracoes


@pytest.fixture
def caminho_tmp(tmp_path: Path) -> Path:
    pasta = tmp_path / "data"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / "lente.sqlite"


@pytest.fixture
def ligacao(caminho_tmp: Path) -> sqlite3.Connection:
    aplicar_migracoes(caminho_tmp)
    lig = abrir_ligacao(caminho_tmp)
    yield lig
    lig.close()


def test_reg_dia_001(ligacao: sqlite3.Connection) -> None:
    """Procura, abertura, feedback e fecho entram por ordem; sem UPDATE/DELETE."""
    from engine.diario.escrever import (
        registar_abertura,
        registar_fecho_dossier,
        registar_feedback,
        registar_procura,
    )
    from engine.diario.ler import ler_diario

    registar_procura(ligacao, {"texto": "Quem aprova o acesso remoto?"})
    registar_abertura(ligacao, {"documento_id": 12})
    registar_feedback(ligacao, {"etiqueta": "positivo"})
    registar_fecho_dossier(ligacao, {"dossier_id": 1})

    entradas = ler_diario(ligacao)
    assert [e["tipo"] for e in entradas] == [
        "procura",
        "abertura",
        "feedback",
        "fecho_dossier",
    ]
    assert entradas[0]["payload"]["texto"] == "Quem aprova o acesso remoto?"

    import engine.diario.escrever as escrever
    import engine.diario.ler as ler

    for nome in (
        "actualizar",
        "atualizar",
        "apagar",
        "eliminar",
        "update",
        "delete",
        "remover",
    ):
        assert not hasattr(escrever, nome)
        assert not hasattr(ler, nome)

    # A API pública não reescreve nem apaga linhas já gravadas.
    assert not any(
        n.startswith("update") or n.startswith("delete") or n.startswith("apagar")
        for n in dir(escrever)
        if not n.startswith("_")
    )


def test_reg_dia_002() -> None:
    """Diário local: sem login, conta remota nem envio pela rede."""
    import engine.diario as pacote
    import engine.diario.escrever as escrever
    import engine.diario.ler as ler

    for nome in ("login", "autenticar", "conta", "upload", "enviar_remoto", "sync"):
        assert not hasattr(pacote, nome)
        assert not hasattr(escrever, nome)
        assert not hasattr(ler, nome)

    proibidos = {
        "urllib",
        "urllib.request",
        "urllib3",
        "requests",
        "httpx",
        "aiohttp",
        "http.client",
        "ftplib",
    }
    for modulo in (escrever, ler):
        fonte = inspect.getsource(modulo)
        arvore = ast.parse(fonte)
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                for alias in no.names:
                    assert alias.name.split(".")[0] not in {
                        "urllib",
                        "urllib3",
                        "requests",
                        "httpx",
                        "aiohttp",
                        "ftplib",
                    }
                    assert alias.name not in proibidos
            if isinstance(no, ast.ImportFrom) and no.module:
                raiz = no.module.split(".")[0]
                assert raiz not in {
                    "urllib",
                    "urllib3",
                    "requests",
                    "httpx",
                    "aiohttp",
                    "ftplib",
                    "http",
                }
