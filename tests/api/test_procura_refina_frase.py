"""Procura FTS refina bloco → frase citável (sem frases no índice FTS)."""

from __future__ import annotations

from pathlib import Path

from starlette.testclient import TestClient

from engine.api.app import criar_app
from engine.ingestao.indexar_minimo import indexar_texto_fts
from engine.ingestao.registo import registar_texto


def test_procura_refina_excerto_a_frase(caminho_tmp: Path, tmp_path: Path) -> None:
    from engine.armazenamento.repositorio import abrir

    ligacao = abrir(caminho_tmp)
    texto = (
        "Primeira frase irrelevante do prólogo. "
        "A Constituição garante direitos fundamentais aos cidadãos. "
        "Última frase de encerramento sem termos."
    )
    destino = tmp_path / "const.txt"
    reg = registar_texto(ligacao, texto, destino)
    indexar_texto_fts(ligacao, documento_id=reg.id, texto=texto)
    ligacao.close()

    app = criar_app(caminho_sqlite=caminho_tmp)
    client = TestClient(app)
    chat = client.post("/chats", json={"titulo": "t"}).json()
    r = client.post(
        "/search",
        json={"chat_id": chat["id"], "texto": "Constituição", "lente": "investigar"},
    )
    assert r.status_code == 200
    eventos = []
    for bloco in r.text.split("\n\n"):
        for linha in bloco.splitlines():
            if linha.startswith("data: "):
                import json

                eventos.append(json.loads(linha[6:]))
    excertos = [e for e in eventos if e.get("tipo") == "excerto"]
    assert excertos
    assert any("Constituição" in (e.get("texto") or "") for e in excertos)
    # Não devolve o documento inteiro como excerto.
    assert all(len(e.get("texto") or "") < len(texto) for e in excertos)
