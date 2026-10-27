"""Download honesto de pesos Hugging Face (Apache / Gemma).

Não inventa ``a_descarregar`` sem iniciar bytes. O escritor (Gemma 4)
só descarrega com ``LENTE_DESCARREGAR_E2B=1``; por omissão devolve
``erro_licenca`` com orientação para pôr o GGUF em ``models/e2b/``.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Any, Callable

from engine.embeddings.carregar import MODELO_ID as EMBEDDING_HF
from engine.embeddings.carregar import pasta_embedding
from engine.juiz.caminhos import (
    FICHEIRO_ARM64,
    FICHEIRO_AVX512,
    MODELO_ID as JUIZ_HF,
    pasta_juiz,
)
from engine.resposta.e2b import (
    ARTEFACTO_GGUF_Q4,
    MODELO_HF_ID as E2B_HF,
    pasta_e2b,
)
from engine.runtime.pesos import Papel, estado_modelos, orientar_falta

_HF_POR_PAPEL: dict[Papel, str] = {
    "embedding": EMBEDDING_HF,
    "juiz": JUIZ_HF,
    "escritor": E2B_HF,
}

_ALLOW_PATTERNS: dict[Papel, list[str] | None] = {
    "embedding": [
        "config.json",
        "config_sentence_transformers.json",
        "modules.json",
        "sentence_bert_config.json",
        "tokenizer*",
        "special_tokens_map.json",
        "model.safetensors",
        "1_Pooling/*",
        "2_Normalize/*",
        "*.py",
        "README*",
    ],
    "juiz": [
        "config.json",
        "tokenizer*",
        "special_tokens_map.json",
        f"onnx/{FICHEIRO_AVX512}",
        f"onnx/{FICHEIRO_ARM64}",
        "onnx/model_qint8_avx512.onnx",
        "onnx/model_quint8_avx2.onnx",
    ],
    "escritor": [ARTEFACTO_GGUF_Q4],
}


def _destino(papel: Papel, raiz: Path) -> Path:
    if papel == "embedding":
        return pasta_embedding(raiz)
    if papel == "juiz":
        return pasta_juiz(raiz)
    return pasta_e2b(raiz)


def _ja_pronto(papel: Papel, raiz: Path) -> bool:
    return estado_modelos(raiz).get(papel, {}).get("estado") == "pronto"


def _eh_erro_licenca(exc: BaseException) -> bool:
    texto = str(exc).casefold()
    return any(
        m in texto
        for m in (
            "gated",
            "401",
            "403",
            "license",
            "licença",
            "licenca",
            "restricted",
            "access to model",
            "authentication",
            "unauthorized",
        )
    )


def _snapshot(repo_id: str, destino: Path, *, allow_patterns: list[str] | None) -> None:
    from huggingface_hub import snapshot_download

    destino.mkdir(parents=True, exist_ok=True)
    kwargs: dict[str, Any] = {
        "repo_id": repo_id,
        "local_dir": str(destino),
    }
    if allow_patterns:
        kwargs["allow_patterns"] = allow_patterns
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        kwargs["token"] = token
    snapshot_download(**kwargs)


def _pos_juiz(destino: Path) -> None:
    for nome in (FICHEIRO_AVX512, FICHEIRO_ARM64, "model_qint8_avx512.onnx"):
        origem = destino / "onnx" / nome
        alvo = destino / nome
        if origem.is_file() and not alvo.is_file():
            alvo.write_bytes(origem.read_bytes())


def _resposta_bloqueio(
    papel: Papel,
    raiz: Path,
    *,
    estado: str,
    mensagem: str | None = None,
) -> dict[str, Any]:
    guia = orientar_falta(raiz, forcar={papel: estado})  # type: ignore[arg-type]
    guia["erro"] = estado
    if mensagem:
        guia["mensagem"] = mensagem
    guia["http_status"] = 409
    return guia


def descarregar_papel(
    papel: Papel,
    *,
    raiz_modelos: Path | str,
    em_fundo: bool = True,
) -> dict[str, Any]:
    """Inicia (ou recusa) o download. Resposta moldável a HTTP-models-download."""
    raiz = Path(raiz_modelos)
    if papel not in _HF_POR_PAPEL:
        return {
            "erro": "pedido_invalido",
            "mensagem": "modelo desconhecido",
            "http_status": 400,
        }

    if _ja_pronto(papel, raiz):
        return {
            "estado": "pronto",
            "modelo": papel,
            "caminho": str(_destino(papel, raiz)),
            "http_status": 200,
        }

    # Gemma: por omissão não arranca bytes (termos HF). REG-MOD-007 / #54.
    if papel == "escritor" and os.environ.get("LENTE_DESCARREGAR_E2B") != "1":
        return _resposta_bloqueio(
            papel,
            raiz,
            estado="erro_licenca",
            mensagem=(
                "Pesos Gemma 4 E2B: aceita a licença no Hugging Face e coloca "
                f"o GGUF Q4 em {pasta_e2b(raiz)}, ou define "
                "LENTE_DESCARREGAR_E2B=1 com token HF."
            ),
        )

    # Offline / testes: não fingir download.
    if os.environ.get("HF_HUB_OFFLINE") == "1" or os.environ.get(
        "LENTE_SEM_DOWNLOAD"
    ) == "1":
        return _resposta_bloqueio(
            papel,
            raiz,
            estado="em_falta",
            mensagem="Download desactivado (offline).",
        )

    destino = _destino(papel, raiz)
    repo = _HF_POR_PAPEL[papel]

    def _trabalho() -> None:
        _snapshot(repo, destino, allow_patterns=_ALLOW_PATTERNS[papel])
        if papel == "juiz":
            _pos_juiz(destino)

    if not em_fundo:
        try:
            _trabalho()
        except Exception as exc:  # noqa: BLE001
            estado = "erro_licenca" if _eh_erro_licenca(exc) else "em_falta"
            return _resposta_bloqueio(
                papel, raiz, estado=estado, mensagem=str(exc)
            )
        return {
            "estado": "pronto",
            "modelo": papel,
            "caminho": str(destino),
            "http_status": 200,
        }

    fio = threading.Thread(
        target=lambda: _trabalho_silencioso(_trabalho),
        name=f"lente-dl-{papel}",
        daemon=True,
    )
    fio.start()
    return {
        "estado": "a_descarregar",
        "modelo": papel,
        "caminho_esperado": str(destino),
        "http_status": 202,
    }


def _trabalho_silencioso(fn: Callable[[], None]) -> None:
    try:
        fn()
    except Exception:
        return


def criar_descarregador(
    raiz_modelos: Path | str,
    *,
    em_fundo: bool = True,
) -> Callable[[str], dict[str, Any]]:
    """Factory injectável em ``criar_app(descarregar_modelo=…)``."""

    raiz = Path(raiz_modelos)

    def _fn(modelo: str) -> dict[str, Any]:
        if modelo not in {"embedding", "juiz", "escritor"}:
            return {
                "erro": "pedido_invalido",
                "mensagem": "modelo desconhecido",
                "http_status": 400,
            }
        return descarregar_papel(
            modelo,  # type: ignore[arg-type]
            raiz_modelos=raiz,
            em_fundo=em_fundo,
        )

    return _fn


__all__ = [
    "criar_descarregador",
    "descarregar_papel",
]
