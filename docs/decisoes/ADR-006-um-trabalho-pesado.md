# ADR-006 — Um trabalho pesado de cada vez

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

Indexação, treino LoRA e procura competem por CPU/GPU. Sem limites, o chat deixa de responder ao rato num portátil de 16 GB.

## Decisão

Um trabalho pesado de cada vez. Uma procura **pausa** indexação e treino e retoma-os no fim. Embedding, juiz e E2B deixam sempre pelo menos **dois núcleos livres** para o sistema e a interface:

- **E2B** (quando escreve) ≤ `nproc − 2`
- **LoRA** ≤ 2 núcleos

As miniaturas do leque são imagens pequenas feitas uma vez na indexação, não um PDF renderizado ao passar o rato.

## Consequências

- A UI continua responsiva durante prosa e treino.
- Indexação e treino demoram mais quando há procuras frequentes; isso é aceite.
- O orçamento de núcleos é contrato de runtime, não sugestão.

## Alternativas rejeitadas

- Correr procura, indexação e LoRA em paralelo no máximo de núcleos.
- Renderizar páginas de PDF sob o cursor para miniaturas.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secção «Orçamento da máquina».
