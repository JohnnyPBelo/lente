"""Regressão REG-BUS-003: identificador literal via FTS5 antes do juiz."""

from __future__ import annotations

from tests.pesquisa.conftest import semear_bloco

from engine.pesquisa.candidatos import unir_candidatos
from engine.pesquisa.fts import indexar_bloco, procurar_fts


def test_reg_bus_003(ligacao) -> None:
    """CVE sintético indexado entra nos candidatos FTS quando a consulta é o termo."""
    termo = "CVE-2099-0001"
    texto = f"O relatório menciona {termo} como referência sintética."
    bloco_id, documento_id, hash_id = semear_bloco(
        ligacao, texto, caminho="/tmp/cve-fts.txt"
    )
    indexar_bloco(
        ligacao,
        bloco_id=bloco_id,
        texto=texto,
        documento_id=documento_id,
        hash_id=hash_id,
    )

    hits = procurar_fts(ligacao, termo)
    assert any(h.origem_id == bloco_id and h.origem == "bloco" for h in hits)

    unidos = unir_candidatos(fts=hits, embedding=[])
    ids = {c.origem_id for c in unidos if c.origem == "bloco"}
    assert bloco_id in ids
