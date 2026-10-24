# ADR-005 — Feedback só no juiz

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

O utilizador corrige highlights (Acertou / Corrigir / Descartar). Essa aprendizagem tem de melhorar a ordenação e o limiar sem tocar no escritor e sem partilhar binários de pesos que interferem entre si.

## Decisão

Feedback afecta **só o juiz**:

- Na hora, perguntas muito parecidas privilegiam trechos confirmados e descem rejeitados entre candidatos já trazidos pela pesquisa. Não se injecta texto no E2B.
- Quando a máquina está livre, um **LoRA rank 8** do juiz rejoga todas as correcções (learning rate baixo, puxão para o modelo base), no máximo dois núcleos. Se as correcções deixadas de lado piorarem, a troca é rejeitada. No fim exporta-se de novo o ONNX e o PyTorch sai da memória.
- **Exportar / importar** é o conjunto de correcções em JSON (versão do formato, id do modelo base, pergunta, trecho, etiqueta, lente, hash do par) — **não** a média nem o binário de adaptadores LoRA.

## Consequências

- O E2B permanece congelado ([ADR-004](ADR-004-e2b-congelado.md)).
- Partilha empilha exemplos úteis num único treino a partir do base; dez LoRAs médios interfeririam.
- Importar exige confirmação; ficheiro de outro modelo base é recusado; Descartar não treina.

## Alternativas rejeitadas

- Treinar ou injectar exemplos no E2B.
- Exportar ou somar ficheiros de pesos LoRA («média de LoRA»).

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secções «Feedback, só no juiz» e «Juntar afinações».
