# Arquitectura

Mapa da arquitectura de execução da Lente. Deriva de [docs/origem/plano.md](../origem/plano.md) e das decisões de fecho em [docs/LEITURA.md](../LEITURA.md). Não reescreve o plano; fecha o «como corre» de forma verificável.

## Ordem de leitura

1. [visao.md](visao.md) — um servidor, três papéis, SQLite único
2. [processos.md](processos.md) — processo Python, Node só no build, escalonador de trabalhos pesados
3. [fluxos.md](fluxos.md) — diagramas de sequência dos gestos principais
4. [escalonador.md](escalonador.md) — um trabalho pesado de cada vez; núcleos e pausas
5. [orcamento.md](orcamento.md) — memória residente, tetos de disco, escritor como visita
6. [falhas.md](falhas.md) — falhas observáveis e o que a UI mostra

## Verificação rápida

| Afirmação | Onde |
| --- | --- |
| Um só servidor em `127.0.0.1:4317` | [visao.md](visao.md), [processos.md](processos.md) |
| Embedding e juiz residentes; E2B visita | [visao.md](visao.md), [orcamento.md](orcamento.md) |
| Um trabalho pesado de cada vez; procura pausa indexação/treino | [escalonador.md](escalonador.md) |
| Sequências de procurar, correlacionar, confrontar, lacunas, alerta, dossier, feedback, LoRA | [fluxos.md](fluxos.md) |
| Estados vazios e recusas (modelo, URL, hash, prosa, LoRA, fila) | [falhas.md](falhas.md) |

## Fora deste pacote

Contratos HTTP, esquema SQL, ADRs numerados, requisitos e planos de implementação vivem noutras pastas (`docs/decisoes/`, `docs/requisitos/`, `docs/dados/`, `docs/planos/`). Este pacote descreve processos, orçamento e fluxos.
