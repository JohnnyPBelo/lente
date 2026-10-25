"""Regressão REG-FOR-004: sem encoder de visão nem stack de áudio."""

from __future__ import annotations

from pathlib import Path

from engine.embeddings.carregar import (
    CONFIG_TEXTO_ONLY,
    carregar_modelo,
)


def test_reg_for_004(tmp_path: Path) -> None:
    """Carga com vision_config/audio_config nulos; OCR continua a ser Tesseract."""
    pasta = tmp_path / "models" / "embeddinggemma-2"
    pasta.mkdir(parents=True)
    (pasta / "config.json").write_text("{}", encoding="utf-8")

    capturado: dict[str, object] = {}

    class ModeloEspiao:
        vision_config = None
        audio_config = None

        def encode(self, textos):
            if isinstance(textos, str):
                return [[0.01] * 768]
            return [[0.01] * 768 for _ in textos]

    def factory(caminho: str, **kwargs):
        capturado["caminho"] = caminho
        capturado["kwargs"] = kwargs
        return ModeloEspiao()

    sessao = carregar_modelo(
        raiz_modelos=tmp_path / "models",
        factory=factory,
        dispositivo="cpu",
    )

    assert capturado["kwargs"]["config_kwargs"] == CONFIG_TEXTO_ONLY
    assert capturado["kwargs"]["config_kwargs"]["vision_config"] is None
    assert capturado["kwargs"]["config_kwargs"]["audio_config"] is None
    assert sessao.vision_config is None
    assert sessao.audio_config is None

    # O OCR de scans não entra neste pacote — continua no motor Tesseract.
    import engine.embeddings as emb

    fonte_pacote = Path(emb.__file__).read_text(encoding="utf-8")
    assert "vision_encoder" not in fonte_pacote.casefold()
    assert "audio_encoder" not in fonte_pacote.casefold()

    from engine.embeddings import carregar as carregar_src

    fonte = Path(carregar_src.__file__).read_text(encoding="utf-8")
    assert "vision_config" in fonte
    assert "audio_config" in fonte
    assert "Tesseract" not in fonte  # OCR não é responsabilidade do embedding
