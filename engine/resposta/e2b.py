"""Escritor Gemma 4 E2B QAT Q4 — visita (sobe, gera, desce). Sem BF16 de treino."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from engine.escalonador.nucleos import limites_cpu
import os

MODELO_HF_ID = "google/gemma-4-E2B-it-qat-q4_0-gguf"
ARTEFACTO_GGUF_Q4 = "gemma-4-E2B-it-qat-q4_0.gguf"
PASTA_E2B = "e2b"

# Nomes / padrões de artefactos de treino ~11 GB — recusados
_RECUSADOS = (
    "bf16",
    "unquantized",
    "safetensors",
    "pytorch_model",
    "11gb",
    "11.4",
)


class PesosE2BAusentes(Exception):
    """GGUF Q4 em falta; o chat segue com excertos e miniaturas."""

    def __init__(self, caminho_manual: str) -> None:
        self.caminho_manual = caminho_manual
        super().__init__(
            "Pesos do E2B ausentes. "
            f"Coloque o GGUF Q4 em: {caminho_manual}"
        )


class ArtefactoRecusado(Exception):
    """Só o GGUF QAT Q4 de visita é aceite (REQ-MOD-006)."""

    def __init__(self, nome: str) -> None:
        self.nome = nome
        super().__init__(
            f"Artefacto recusado: {nome!r}. "
            f"Só se aceita o GGUF Q4 de visita ({ARTEFACTO_GGUF_Q4}); "
            "não se descarregam os ~11 GB BF16 de treino."
        )


def pasta_e2b(raiz_modelos: Path | str | None = None) -> Path:
    raiz = Path(raiz_modelos) if raiz_modelos is not None else Path("models")
    return Path(raiz) / PASTA_E2B


def caminho_gguf(raiz_modelos: Path | str | None = None) -> Path:
    return pasta_e2b(raiz_modelos) / ARTEFACTO_GGUF_Q4


def artefactos_aceites() -> list[str]:
    """Lista canónica: apenas o GGUF Q4 de visita."""
    return [ARTEFACTO_GGUF_Q4]


def validar_artefacto(nome: str) -> str:
    """Aceita o Q4 de visita; recusa BF16 / unquantized / safetensors de treino."""
    base = Path(nome).name
    lower = base.casefold()
    if lower == ARTEFACTO_GGUF_Q4.casefold() or (
        "q4" in lower and "gguf" in lower and "e2b" in lower and "bf16" not in lower
    ):
        return ARTEFACTO_GGUF_Q4
    for marcador in _RECUSADOS:
        if marcador in lower:
            raise ArtefactoRecusado(nome)
    if lower.endswith(".gguf") and "q4" in lower:
        return ARTEFACTO_GGUF_Q4
    raise ArtefactoRecusado(nome)


def _n_threads_omissao() -> int:
    nproc = os.cpu_count() or 2
    try:
        return limites_cpu(nproc)["e2b_max"]
    except ValueError:
        return max(1, nproc - 2)


class EscritorE2B:
    """Runtime de visita do E2B. Congelado — sem fine-tune / LoRA."""

    congelado: bool = True

    def __init__(
        self,
        *,
        raiz_modelos: Path | str | None = None,
        factory: Callable[..., Any] | None = None,
        n_threads: int | None = None,
    ) -> None:
        self._raiz = Path(raiz_modelos) if raiz_modelos is not None else Path("models")
        self._factory = factory
        self._n_threads = n_threads if n_threads is not None else _n_threads_omissao()
        self._modelo: Any | None = None

    def disponivel(self) -> bool:
        return caminho_gguf(self._raiz).is_file()

    @property
    def residente(self) -> bool:
        return self._modelo is not None

    def carregar(self) -> None:
        """Sobe o GGUF Q4. Não descarrega da rede; não aceita BF16."""
        destino = caminho_gguf(self._raiz)
        validar_artefacto(destino.name)
        if self._factory is not None:
            self._modelo = self._factory(
                str(destino),
                n_threads=self._n_threads,
            )
            return
        if not destino.is_file():
            raise PesosE2BAusentes(str(destino))
        # Carga real só quando llama-cpp está instalado e o ficheiro existe.
        # Testes de CI usam ``factory`` (double) — nunca descarregam GGUF.
        from llama_cpp import Llama  # type: ignore[import-untyped]

        self._modelo = Llama(
            model_path=str(destino),
            n_threads=self._n_threads,
            verbose=False,
        )

    def gerar(self, prompt: str, *, max_tokens: int = 512) -> str:
        if self._modelo is None:
            raise RuntimeError("E2B não está carregado; chame carregar() antes.")
        if hasattr(self._modelo, "create_completion"):
            saida = self._modelo.create_completion(
                prompt,
                max_tokens=max_tokens,
                temperature=0.2,
            )
            return str(saida["choices"][0]["text"]).strip()
        # Double que é ele próprio invocável como completion
        return str(self._modelo(prompt)).strip()

    def libertar(self) -> None:
        """Desce o E2B da RAM de trabalho (fim da visita)."""
        if self._modelo is None:
            return
        close = getattr(self._modelo, "close", None)
        if callable(close):
            close()
        self._modelo = None
