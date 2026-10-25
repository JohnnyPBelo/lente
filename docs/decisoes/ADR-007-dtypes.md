# ADR-007 — Dtypes dos modelos

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

EmbeddingGemma em float16 na CPU produz NaN. O juiz tem de ser leve o suficiente para residir. A GPU, se existir, acelera o mesmo código — não há um segundo modo.

## Decisão

| Componente | Dtype |
| --- | --- |
| EmbeddingGemma em CPU | **float32** |
| EmbeddingGemma em GPU | **bfloat16** |
| EmbeddingGemma em float16 | **excluído** (NaN) |
| Juiz no dia a dia | **ONNX int8** |
| Juiz só durante LoRA | PyTorch (entra e sai da memória) |

## Consequências

- Vectores estáveis na CPU; GPU usa bfloat16 sem caminho float16.
- Juiz residente ~120 MB; PyTorch só no treino.
- Um único código de caminho; a GPU só acelera.

## Alternativas rejeitadas

- float16 para EmbeddingGemma (NaN observados).
- Manter o juiz em float32/PyTorch residente no dia a dia.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secções «Três papéis, dois residentes» e «Que modelo faz de System One».
