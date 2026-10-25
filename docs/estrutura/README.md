# Estrutura futura

Mapa dos caminhos e dos módulos da Lente. Deriva de [docs/origem/plano.md](../origem/plano.md) e das decisões de fecho em [docs/LEITURA.md](../LEITURA.md). Não cria código: descreve o que a implementação vai ocupar.

## Um só processo HTTP

O motor Python escuta em `127.0.0.1:4317` e serve a UI já construída. Node 22 só constrói. Não há Electron nem segundo servidor.

## Conteúdo desta pasta

| Ficheiro | Conteúdo |
| --- | --- |
| [arvore.md](arvore.md) | Árvore futura de pastas e o papel de cada caminho |
| [modulos.md](modulos.md) | Contratos por módulo (`MOD-…`): responsabilidade, entradas, saídas, fora de âmbito |
| [contrato-http.md](contrato-http.md) | Endpoints HTTP (`HTTP-…`) com formas JSON sintéticas |

## Ordem sugerida

1. `arvore.md` — onde vive cada peça
2. `modulos.md` — o que cada peça faz e não faz
3. `contrato-http.md` — como a UI fala com o motor

## Relação com o resto da especificação

- Requisitos e ADRs fecham lacunas do plano; esta pasta não as reabre.
- Exemplos de JSON e IDs são sintéticos. Não copiam documentos reais nem pesos.
- Runtime (`data/`, `models/`) fica fora do Git; a especificação fica em `docs/`.
