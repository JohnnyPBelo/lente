# ADR-001 — Três papéis, dois residentes

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

A app tem de encontrar trechos, decidir o que merece highlight e escrever prosa citada, num portátil de 16 GB sem deixar a máquina presa. Carregar três modelos grandes ao mesmo tempo esgota a RAM.

## Decisão

Três papéis distintos:

1. **EmbeddingGemma 2 (270M, só texto)** — encontra. Congelado e residente.
2. **Juiz cross-encoder em ONNX int8 (118M)** — decide o highlight. Residente e leve.
3. **Gemma 4 E2B QAT Q4** — escreve a resposta. Congelado; sobe para a resposta e desce a seguir (visita).

Só EmbeddingGemma e o juiz ficam residentes numa procura. O E2B é visita. Visão e áudio não se carregam.

## Consequências

- Orçamento residente previsível: sistema, browser, EmbeddingGemma, juiz int8, SQLite.
- Disco aproximado: 2 GB + 0,5 GB + 3 GB; não se descarregam os 11 GB de pesos de treino do E2B.
- A prosa só existe quando o E2B está carregado; sem ele, o chat segue com excertos e miniaturas.

## Alternativas rejeitadas

- Manter o E2B residente — custa RAM demais no alvo de 16 GB.
- Um único modelo para encontrar, decidir e escrever — mistura papéis e impede o juiz leve residente.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secções «Três papéis, dois residentes» e «Orçamento da máquina».
