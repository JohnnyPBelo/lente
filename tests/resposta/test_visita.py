"""Regressão REG-RES-010: E2B é visita; feedback não altera pesos do escritor."""

from __future__ import annotations

from engine.resposta.e2b import EscritorE2B


class _GgufDuplo:
    """Double do runtime GGUF: sem pesos reais nem download."""

    def __init__(self) -> None:
        self.libertado = False
        self.n_threads: int | None = None

    def __call__(self, *_a, **kw):
        self.n_threads = kw.get("n_threads")
        return self

    def create_completion(self, *_a, **_k):
        return {
            "choices": [
                {
                    "text": (
                        "O acesso remoto exige aprovação do responsável. [1]"
                    )
                }
            ]
        }

    def close(self) -> None:
        self.libertado = True


def test_reg_res_010(tmp_path) -> None:
    """Após geração, libertar() deixa o E2B sem residência; sem fine-tune."""
    gguf = tmp_path / "models" / "e2b" / "gemma-4-E2B-it-qat-q4_0.gguf"
    gguf.parent.mkdir(parents=True)
    gguf.write_bytes(b"GGUF-fake")

    duplo = _GgufDuplo()
    escritor = EscritorE2B(
        raiz_modelos=tmp_path / "models",
        factory=duplo,
        n_threads=2,
    )
    assert escritor.residente is False

    escritor.carregar()
    assert escritor.residente is True
    texto = escritor.gerar("prompt sintético")
    assert "[1]" in texto

    escritor.libertar()
    assert escritor.residente is False
    assert duplo.libertado is True

    # Feedback não altera pesos do E2B (congelado — sem API de treino)
    assert not hasattr(escritor, "treinar")
    assert not hasattr(escritor, "aplicar_lora")
    assert escritor.congelado is True
