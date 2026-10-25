"""Regressão REG-BUS-006: um SQLite; cópia preserva FTS e vectores."""

from __future__ import annotations

import shutil
from pathlib import Path

from tests.pesquisa.conftest import semear_bloco

from engine.armazenamento.repositorio import abrir
from engine.pesquisa.fts import indexar_bloco, procurar_fts
from engine.pesquisa.vec import DIMENSOES, guardar_vector, normalizar, procurar_cosseno


def test_reg_bus_006(caminho_tmp: Path, tmp_path: Path) -> None:
    """Copiar o ficheiro e reabrir responde sem reindexar; sem base vectorial à parte."""
    termo = "CVE-2099-0001"
    texto = f"Bloco com {termo}."
    vector = normalizar([1.0] + [0.0] * (DIMENSOES - 1))

    ligacao = abrir(caminho_tmp)
    bloco_id, documento_id, hash_id = semear_bloco(
        ligacao, texto, caminho="/tmp/mesmo-ficheiro.txt"
    )
    indexar_bloco(
        ligacao,
        bloco_id=bloco_id,
        texto=texto,
        documento_id=documento_id,
        hash_id=hash_id,
    )
    guardar_vector(ligacao, bloco_id=bloco_id, hash_id=hash_id, vector=vector)
    ligacao.close()

    copia = tmp_path / "copia" / "lente.sqlite"
    copia.parent.mkdir(parents=True)
    shutil.copy2(caminho_tmp, copia)

    reaberta = abrir(copia, aplicar=False)
    hits = procurar_fts(reaberta, termo)
    assert any(h.origem_id == bloco_id for h in hits)
    vizinhos = procurar_cosseno(reaberta, vector, limite=5)
    assert vizinhos and vizinhos[0].bloco_id == bloco_id
    reaberta.close()

    # Sem segundo processo / cliente de base vectorial externa.
    import engine.pesquisa as pacote
    import engine.pesquisa.vec as mod_vec

    texto_pack = Path(pacote.__file__).read_text(encoding="utf-8")
    texto_vec = Path(mod_vec.__file__).read_text(encoding="utf-8")
    proibidos = ("qdrant", "chromadb", "chroma", "lancedb", "psycopg", "postgres")
    combinado = (texto_pack + texto_vec).casefold()
    for nome in proibidos:
        assert nome not in combinado
