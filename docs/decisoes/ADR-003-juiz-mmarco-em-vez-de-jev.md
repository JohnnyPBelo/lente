# ADR-003 — Juiz mmarco-mMiniLMv2 no lugar do Jev

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

O Jev (`jev-1.14.0`) é o System One da TypeSafe e só existe na API deles: não há pesos para instalar. Um clone local (Qwen ~4B ≈ 9 GB ou DeBERTa grande ≈ 1 GB) soma-se aos modelos que a app já carrega e faz um portátil de 16 GB arrastar. O papel necessário é decisão rápida sem prosa: «esta frase responde ou não».

## Decisão

O juiz é o cross-encoder [`cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`](https://huggingface.co/cross-encoder/mmarco-mMiniLMv2-L12-H384-v1) (118M, Apache 2.0, mMARCO incluindo português). No dia a dia corre o ONNX int8 já publicado (~120 MB). Não é o Jev e não traz a calibração dele; a pontuação ajusta-se com feedback só neste modelo ([ADR-005](ADR-005-feedback-so-no-juiz.md)).

## Consequências

- Cabe no orçamento de 16 GB junto com EmbeddingGemma residente e E2B visita.
- Calibração e limiar começam sem o perfil do Jev; o feedback do utilizador é o caminho de afinação.
- O highlight continua a ser pintado pelo código a partir de intervalos literais do ficheiro.

## Alternativas rejeitadas

- API Jev remota — exige rede e contas; fora da superfície local ([ADR-008](ADR-008-superficie-local.md)).
- Clones locais do System One (Qwen ~4B, DeBERTa grande) — RAM a mais no alvo de 16 GB.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secção «Que modelo faz de System One».
