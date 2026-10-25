# ADR-016 — Fora de âmbito

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

O plano lista explicitamente o que fica de fora porque pesa, muda o modelo ou altera a superfície de segurança. Sem um ADR, estas exclusões diluem-se em issues futuras.

## Decisão

Ficam **fora de âmbito** (não implementar nesta linha de produto):

- base vectorial separada
- índice aproximado
- Vec1
- reavaliar a biblioteca inteira (em fundo)
- média de LoRA (somar/averaging de pesos)
- encoder de visão
- outro modelo de decisão (incluindo Jev e clones locais)
- exemplos no prompt do E2B
- fine-tune do E2B
- contas, permissões e sincronização
- áudio
- geração de procedimentos de ataque

## Consequências

- PRs e requisitos que toquem nestes itens são rejeitados por âmbito, não por «ainda não».
- Segurança: geração de procedimentos de ataque está excluída de propósito.
- Qualquer reabertura exige ADR novo que superseda este ou o ADR específico relacionado.

## Alternativas rejeitadas

- Tratar a lista como «depois» implícito sem registo.
- Reabrir Jev, ANN ou fine-tune E2B sem nova decisão formal.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secção «De fora, porque pesa ou muda o modelo».
