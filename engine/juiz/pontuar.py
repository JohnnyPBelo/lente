"""Pontuação de pares (pergunta, frase) com o juiz ONNX — sem prosa nem stack de treino."""

from __future__ import annotations

from typing import Any, Protocol, Sequence


class _SessaoAvaliavel(Protocol):
    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]: ...


def pontuar(
    pergunta: str,
    lista_frases: Sequence[str],
    *,
    sessao: _SessaoAvaliavel,
) -> list[float]:
    """Devolve um score por frase. Caminho quente sem stack de treino residente."""
    if not lista_frases:
        return []
    scores = sessao.avaliar(pergunta, lista_frases)
    if len(scores) != len(lista_frases):
        raise ValueError(
            f"Esperava {len(lista_frases)} scores, obtive {len(scores)}"
        )
    return [float(s) for s in scores]


def pontuar_com_sessao_onnx(
    pergunta: str,
    frases: Sequence[str],
    *,
    sessao_onnx: Any,
    tokenizador: Any,
    max_length: int = 512,
) -> list[float]:
    """Corre o batch no ONNX Runtime a partir de um tokenizador local."""
    import numpy as np

    if tokenizador is None:
        raise RuntimeError("Tokenizador do juiz em falta para pontuação ONNX.")

    input_ids: list[list[int]] = []
    attention_mask: list[list[int]] = []
    for frase in frases:
        codificado = _codificar_par(
            tokenizador,
            pergunta,
            frase,
            max_length=max_length,
        )
        input_ids.append(codificado["input_ids"])
        attention_mask.append(codificado["attention_mask"])

    alimentacao: dict[str, Any] = {
        "input_ids": np.asarray(input_ids, dtype=np.int64),
        "attention_mask": np.asarray(attention_mask, dtype=np.int64),
    }
    nomes_entrada = {i.name for i in sessao_onnx.get_inputs()}
    if "token_type_ids" in nomes_entrada:
        alimentacao["token_type_ids"] = np.zeros_like(alimentacao["input_ids"])

    saidas = sessao_onnx.run(None, alimentacao)
    logits = np.asarray(saidas[0])
    if logits.ndim == 2 and logits.shape[-1] == 1:
        logits = logits[:, 0]
    return [float(x) for x in logits.tolist()]


def _codificar_par(
    tokenizador: Any,
    pergunta: str,
    frase: str,
    *,
    max_length: int,
) -> dict[str, list[int]]:
    """Codifica o par no formato do cross-encoder (sequência única com SEP)."""
    # API tokenizers.Tokenizer (Hugging Face fast)
    if hasattr(tokenizador, "encode"):
        # XLM-R / MiniLM: <s> pergunta </s></s> frase </s>
        texto = f"{pergunta}</s></s>{frase}"
        encoding = tokenizador.encode(texto)
        ids = list(encoding.ids)[:max_length]
        mask = [1] * len(ids)
        if len(ids) < max_length:
            pad_id = 1  # <pad> típico XLM-R
            if hasattr(tokenizador, "token_to_id"):
                pad = tokenizador.token_to_id("<pad>")
                if pad is not None:
                    pad_id = pad
            ids = ids + [pad_id] * (max_length - len(ids))
            mask = mask + [0] * (max_length - len(mask))
        return {"input_ids": ids, "attention_mask": mask}

    # Fallback estilo transformers BatchEncoding
    encoding = tokenizador(
        pergunta,
        frase,
        padding="max_length",
        truncation=True,
        max_length=max_length,
        return_tensors=None,
    )
    return {
        "input_ids": list(encoding["input_ids"]),
        "attention_mask": list(encoding["attention_mask"]),
    }
