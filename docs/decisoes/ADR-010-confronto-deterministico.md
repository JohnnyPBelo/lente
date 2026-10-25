# ADR-010 — Confronto determinístico sem modelo novo

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

O modo Confrontar pede se dois trechos concordam, se contradizem ou se falam de assuntos diferentes. Um terceiro modelo (NLI dedicado ou LLM) sairia do orçamento de 16 GB e da regra dos três papéis.

## Decisão

Confronto **determinístico**, sem modelo novo. A leitura é função de:

1. as **duas direcções** do juiz (A→B e B→A), e
2. o **cosseno** entre os dois trechos,

mapeadas para **concordam** / **contradizem-se** / **assuntos diferentes**. Limiares e exemplos sintéticos ficam no contrato do confronto. A lente de trabalho não altera estas três leituras.

## Consequências

- Reutiliza o juiz residente e os vectores já indexados.
- Resultado reproduzível para os mesmos trechos e a mesma versão do juiz.
- Sem descarga nem residente adicional.

## Alternativas rejeitadas

- Modelo NLI ou LLM só para confronto.
- Pedir a classificação em prosa ao E2B.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — modo Confrontar em «A barra de escrita»; fecho em [docs/LEITURA.md](../LEITURA.md).
