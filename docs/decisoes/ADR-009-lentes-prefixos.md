# ADR-009 — Lentes → prefixos EmbeddingGemma 2

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

As lentes de trabalho (investigar, assessment, acreditação, verificar) e o modo Procurar mudam o sentido da query. O EmbeddingGemma 2 exige prefixos de tarefa; a prosa de cada lente não deve contaminar o embedding nem chamar o E2B onde o plano não o prevê.

## Decisão

Mapeamento lente/modo → prefixo de query:

| Uso | Prefixo EmbeddingGemma 2 |
| --- | --- |
| Procurar (pesquisa curta) | `task: search result \| query: …` |
| Investigar, acreditação | `task: question answering \| query: …` |
| Verificar, assessment | `task: fact checking \| query: …` |
| Documento (indexação) | `title: {título} \| text: {conteúdo}` |

A **instrução de prosa** de cada lente entra **só no E2B**. **Alerta** e **lacunas** não chamam o E2B. A lente não muda o confronto ([ADR-010](ADR-010-confronto-deterministico.md)).

## Consequências

- Retrieval alinhado ao tipo de pergunta sem segundo encoder.
- Alerta e lacunas ficam só com embedding + juiz + FTS; respostas em lista/excertos.
- Contrato de prefixos fica estável para testes e rastreio.

## Alternativas rejeitadas

- Um único prefixo para todas as lentes.
- Meter a prosa da lente no embedding ou chamar E2B em alerta/lacunas.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secções «A barra de escrita» e «Pesquisa, sem modelo a mais»; fecho em [docs/LEITURA.md](../LEITURA.md).
