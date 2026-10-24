# ADR-004 — E2B congelado

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

O escritor (Gemma 4 E2B QAT Q4) gera prosa presa a trechos. Reaproveitar respostas antigas, exemplos confirmados ou fine-tune do escritor misturaria conhecimento inventado com prova e aumentaria o risco de alucinação citada.

## Decisão

O E2B fica **congelado**. Em cada procura vê só: os trechos que o juiz deixou passar (com ficheiro e página), o texto dessas páginas, e eventualmente a página aberta no leitor se a pergunta for sobre ela. Não vê a biblioteca inteira, prosa que escreveu antes, nem exemplos de respostas confirmadas. Não há fine-tune do escritor. Perguntas anteriores no mesmo chat servem só para reescrever a procura de seguimento; a resposta nova tem de citar trechos desta volta.

## Consequências

- Cada resposta é independente da prosa anterior; a prova fica amarrada aos trechos desta procura.
- Sem descarregar os 11 GB de pesos de treino do E2B.
- Afinação de qualidade de citação passa pelo juiz e pelas duas portas ([ADR-011](ADR-011-frase-depois-das-duas-portas.md)), não pelo escritor.

## Alternativas rejeitadas

- Injectar prosa anterior ou exemplos no prompt do E2B.
- Fine-tune do E2B com respostas confirmadas.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secções «Três papéis, dois residentes» e «A resposta, sem reaproveitar respostas velhas».
