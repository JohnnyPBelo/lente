"""Cache residente de EmbeddingGemma — evita recarregar pesos a cada ingestão."""

from __future__ import annotations

from pathlib import Path

from engine.embeddings import carregar as carregar_mod


class _ModeloFake:
    vision_config = None
    audio_config = None

    def encode(self, textos):  # noqa: ANN001
        n = len(textos) if not isinstance(textos, str) else 1
        return [[0.1] * carregar_mod.DIMENSAO_NATIVA for _ in range(n)]


def test_carregar_modelo_reutiliza_sessao(tmp_path: Path) -> None:
    raiz = tmp_path / "models"
    pasta = raiz / carregar_mod.PASTA_MODELO
    pasta.mkdir(parents=True)
    (pasta / "config.json").write_text("{}", encoding="utf-8")
    (pasta / "model.safetensors").write_bytes(b"x")

    chamadas = {"n": 0}

    def factory(caminho: str, **kwargs):  # noqa: ANN003
        del caminho, kwargs
        chamadas["n"] += 1
        return _ModeloFake()

    carregar_mod.limpar_cache_sessoes()
    # Com factory= o cache residente fica desligado (doubles de teste).
    a = carregar_mod.carregar_modelo(
        raiz_modelos=raiz, dispositivo="cpu", factory=factory
    )
    b = carregar_mod.carregar_modelo(
        raiz_modelos=raiz, dispositivo="cpu", factory=factory
    )
    assert chamadas["n"] == 2
    assert a is not b

    # Sem factory: primeira carga cria; segunda devolve a mesma sessão.
    carregar_mod.limpar_cache_sessoes()
    contagens = {"n": 0}

    def factory_cache(caminho: str, **kwargs):  # noqa: ANN003
        del caminho, kwargs
        contagens["n"] += 1
        return _ModeloFake()

    # Forçamos o caminho «real» substituindo o factory por omissão via monkey
    # local: carregar_modelo só usa factory injectada; para exercitar o cache
    # sem HF, patchamos _factory_sentence_transformers.
    original = carregar_mod._factory_sentence_transformers
    carregar_mod._factory_sentence_transformers = factory_cache  # type: ignore[assignment]
    try:
        s1 = carregar_mod.carregar_modelo(raiz_modelos=raiz, dispositivo="cpu")
        s2 = carregar_mod.carregar_modelo(raiz_modelos=raiz, dispositivo="cpu")
        assert contagens["n"] == 1
        assert s1 is s2
    finally:
        carregar_mod._factory_sentence_transformers = original  # type: ignore[assignment]
        carregar_mod.limpar_cache_sessoes()
