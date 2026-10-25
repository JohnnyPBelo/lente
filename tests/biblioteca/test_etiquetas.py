"""Regressão REG-BIB-001 e REG-BIB-002: etiquetas e tipo manual."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from engine.armazenamento.ligacao import abrir_ligacao
from engine.armazenamento.migracoes import aplicar_migracoes


def _agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _inserir_documento(
    ligacao: sqlite3.Connection,
    *,
    caminho: str,
    titulo: str,
    tipo: str = "",
    tipo_sugerido: str | None = None,
    estado: str = "ok",
) -> int:
    instante = _agora()
    cur = ligacao.execute(
        """
        INSERT INTO documentos (
            caminho, titulo, tipo, tipo_sugerido, sha256, estado,
            criado_em, actualizado_em
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            caminho,
            titulo,
            tipo,
            tipo_sugerido,
            "a" * 64,
            estado,
            instante,
            instante,
        ),
    )
    ligacao.commit()
    return int(cur.lastrowid)


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


def test_reg_bib_001(ligacao: sqlite3.Connection) -> None:
    """Etiquetas persistem; filtro por etiqueta devolve só quem as tem."""
    from engine.biblioteca.etiquetas import definir_etiquetas, etiquetas_de
    from engine.biblioteca.filtrar import listar_documentos

    doc_a = _inserir_documento(ligacao, caminho="/tmp/a.pdf", titulo="A")
    doc_b = _inserir_documento(ligacao, caminho="/tmp/b.pdf", titulo="B")
    doc_c = _inserir_documento(ligacao, caminho="/tmp/c.pdf", titulo="C")

    definir_etiquetas(ligacao, doc_a, ["acesso", "vpn"])
    definir_etiquetas(ligacao, doc_b, ["acesso"])
    definir_etiquetas(ligacao, doc_c, ["outro"])

    assert etiquetas_de(ligacao, doc_a) == ["acesso", "vpn"]
    assert set(etiquetas_de(ligacao, doc_b)) == {"acesso"}

    filtrados = listar_documentos(ligacao, etiqueta="acesso")
    ids = {item["id"] for item in filtrados}
    assert ids == {doc_a, doc_b}
    for item in filtrados:
        assert "acesso" in item["etiquetas"]


def test_reg_bib_002(ligacao: sqlite3.Connection) -> None:
    """Filtro por tipo usa a escolha manual; sugestão não a substitui."""
    from engine.biblioteca.filtrar import (
        definir_tipo_manual,
        listar_documentos,
        sugerir_tipo,
    )

    doc = _inserir_documento(
        ligacao,
        caminho="/tmp/politica.pdf",
        titulo="Politica",
        tipo="manual",
    )
    sugerir_tipo(ligacao, doc, "politica")

    linha = ligacao.execute(
        "SELECT tipo, tipo_sugerido FROM documentos WHERE id = ?",
        (doc,),
    ).fetchone()
    assert linha["tipo"] == "manual"
    assert linha["tipo_sugerido"] == "politica"

    # Sugestão sem confirmação não altera o tipo manual.
    sugerir_tipo(ligacao, doc, "procedimento")
    linha = ligacao.execute(
        "SELECT tipo, tipo_sugerido FROM documentos WHERE id = ?",
        (doc,),
    ).fetchone()
    assert linha["tipo"] == "manual"
    assert linha["tipo_sugerido"] == "procedimento"

    outro = _inserir_documento(
        ligacao,
        caminho="/tmp/outro.pdf",
        titulo="Outro",
        tipo="relatorio",
        tipo_sugerido="politica",
    )
    definir_tipo_manual(ligacao, outro, "relatorio")

    por_tipo = listar_documentos(ligacao, tipo="manual")
    assert {item["id"] for item in por_tipo} == {doc}
    assert all(item["tipo"] == "manual" for item in por_tipo)
    # tipo_sugerido não entra no filtro de tipo.
    assert listar_documentos(ligacao, tipo="politica") == []
