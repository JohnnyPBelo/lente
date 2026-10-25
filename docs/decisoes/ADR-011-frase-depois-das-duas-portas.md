# ADR-011 — Frase só depois das duas portas

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

Mostrar prosa do E2B antes de validar citação e fidelidade criaria texto provisório a apagar — má prova e UX confusa.

## Decisão

Uma frase só aparece no fio depois de passar as **duas portas**:

1. acaba com `[n]` de um trecho que estava no pacote desta procura;
2. o juiz compara a frase com o trecho citado e confirma fidelidade.

Se nenhuma frase sobreviver: ficam excertos e miniaturas, ou só o aviso de vazio. **Miniaturas podem aparecer primeiro.** **Não há prosa provisória** a ser removida depois.

## Consequências

- O fio nunca mostra prosa sem prova filtrada.
- Latência percebida: miniaturas/excertos antes da prosa final.
- Implementação de streaming tem de bufferizar prosa até às portas, não emitir tokens crus no chat.

## Alternativas rejeitadas

- Stream de prosa provisória com reescrita/apagamento posterior.
- Mostrar a frase só com a porta `[n]` e saltar o juiz.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secção «A resposta, sem reaproveitar respostas velhas»; fecho em [docs/LEITURA.md](../LEITURA.md).
