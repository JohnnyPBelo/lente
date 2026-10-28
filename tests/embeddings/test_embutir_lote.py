"""Batch de embeddings — menos passes no modelo sob volume."""

from __future__ import annotations

from pathlib import Path

from engine.embeddings import carregar as carregar_mod


class _ModeloFake:
    vision_config = None
    audio_config = None
    chamadas: list[int]

    def __init__(self) -> None:
        self.chamadas = []

    def encode(self, textos):  # noqa: ANN001
        lote = [textos] if isinstance(textos, str) else list(textos)
        self.chamadas.append(len(lote))
        return [[0.2] * carregar_mod.DIMENSAO_NATIVA for _ in lote]


def test_embutir_lote_agrupa_passes() -> None:
    modelo = _ModeloFake()
    sessao = carregar_mod.SessaoEmbedding(
        modelo_id="fake",
        caminho=Path("."),
        dispositivo="cpu",
        dtype="float32",
        vision_config=None,
        audio_config=None,
        _modelo=modelo,
    )
    textos = [f"texto {i}" for i in range(40)]
    vectores = carregar_mod.embutir_lote(textos, sessao=sessao, tamanho_lote=16)
    assert len(vectores) == 40
    assert all(len(v) == carregar_mod.DIMENSAO for v in vectores)
    # 40 textos / 16 → 3 passes (16+16+8), não 40.
    assert modelo.chamadas == [16, 16, 8]
    assert sum(modelo.chamadas) == 40
