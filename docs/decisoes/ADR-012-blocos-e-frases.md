# ADR-012 — Blocos para embedding, frases para highlight

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

O plano de origem deixa a granularidade de indexação implícita. Embedding por frase é caro e ruidoso; highlight por bloco longo é impreciso no leitor.

## Decisão

- **Unidade de embedding:** bloco de cerca de **500 tokens** do tokenizador do EmbeddingGemma, com **sobreposição de 50**.
- **Unidade de highlight e de julgamento:** a **frase**, com **offsets** e **caixas** gravados na ingestão.

Quem pinta o highlight é o código: cada marca é um intervalo literal do ficheiro.

## Consequências

- Retrieval opera sobre blocos; o juiz e o leitor operam sobre frases citáveis.
- Dossier e export guardam offsets/caixas por frase.
- Overlap 50 reduz cortes no meio de cláusulas sem duplicar o índice em demasia.

## Alternativas rejeitadas

- Embedding só por frase (custo e fragmentação).
- Highlight ao nível do bloco inteiro sem offsets de frase.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secção «Entradas»; fecho em [docs/LEITURA.md](../LEITURA.md).
