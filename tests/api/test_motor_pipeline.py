"""#47 — com juiz em disco selecciona pipeline; sem pesos fica FTS."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.api.motor import selecionar_motor_procura
from engine.armazenamento.repositorio import abrir
from engine.ingestao.indexar_minimo import indexar_texto_fts
from engine.ingestao.registo import registar_ficheiro


def test_selecionar_sem_pesos_usa_fts(tmp_path: Path) -> None:
    sqlite = tmp_path / "lente.sqlite"
    modelos = tmp_path / "models"
    modelos.mkdir()
    motor = selecionar_motor_procura(sqlite, raiz_modelos=modelos)
    assert getattr(motor, "modo", None) == "fts"


def test_selecionar_com_juiz_usa_pipeline(tmp_path: Path) -> None:
    sqlite = tmp_path / "lente.sqlite"
    modelos = tmp_path / "models"
    juiz = modelos / "juiz"
    juiz.mkdir(parents=True)
    (juiz / "model_qint8_avx512_vnni.onnx").write_bytes(b"fake-onnx")
    motor = selecionar_motor_procura(sqlite, raiz_modelos=modelos)
    assert getattr(motor, "modo", None) == "pipeline"


def test_pipeline_com_double_juiz_pontua(
    caminho_tmp: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """FTS + juiz injectável: score_juiz deixa de ser sempre 1.0."""
    amostra = tmp_path / "doc.txt"
    amostra.write_text(
        "A política de acesso local exige prova na página citada.",
        encoding="utf-8",
    )
    ligacao = abrir(caminho_tmp)
    reg = registar_ficheiro(ligacao, amostra)
    indexar_texto_fts(
        ligacao,
        documento_id=reg.id,
        texto=amostra.read_text(encoding="utf-8"),
        pasta_miniaturas=tmp_path / "thumbs",
    )

    class JuizFixo:
        def avaliar(self, pergunta: str, frases):
            del pergunta
            return [0.75 for _ in frases]

    modelos = tmp_path / "models"
    (modelos / "juiz").mkdir(parents=True)
    (modelos / "juiz" / "model_qint8_avx512_vnni.onnx").write_bytes(b"x")

    monkeypatch.setattr(
        "engine.juiz.carregar.carregar_sessao",
        lambda **_kwargs: JuizFixo(),
    )

    from engine.api.motor import motor_procura_pipeline

    motor = motor_procura_pipeline(
        caminho_tmp, raiz_modelos=modelos, com_embedding=False
    )
    resultado = motor(
        chat_id="cht_1",
        texto="política de acesso",
        lente="investigar",
        com_e2b=False,
    )

    assert resultado["motor"] == "pipeline"
    assert resultado["excertos"], resultado
    assert resultado["excertos"][0]["score_juiz"] == 0.75
