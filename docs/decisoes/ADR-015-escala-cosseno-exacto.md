# ADR-015 — Escala: cosseno exacto mantém-se

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

Com milhares de documentos e vectores de 256 dimensões, o varrimento exacto cabe em milissegundos. Mais tarde pode deixar de caber. A tentação seria um índice aproximado (ANN), que pode omitir o trecho certo — o mesmo motivo que exclui Vec1 ([ADR-002](ADR-002-sqlite-fts5-sqlite-vec.md)).

## Decisão

Escala alvo: **milhares de documentos**. A pesquisa permanece **cosseno exacto**. Se o varrimento **deixar de caber em milissegundos**, a correcção **mantém-se exacta**; **não** se troca por índice aproximado.

## Consequências

- Garantia de não saltar vizinhos, mesmo sob latência maior.
- Se a biblioteca crescer muito além do alvo, a resposta é outra arquitectura consciente — não ANN silencioso.
- Lista da biblioteca virtualizada na UI para milhares de ficheiros.

## Alternativas rejeitadas

- Índice aproximado (HNSW, IVF, Vec1, etc.) quando o exacto ficar lento.
- Reavaliar a biblioteca inteira em fundo para «reparar» omissões de ANN.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secção «Base vectorial»; fecho em [docs/LEITURA.md](../LEITURA.md).
