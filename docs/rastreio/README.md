# Matriz de rastreio

Liga cada secção de [docs/origem/plano.md](../origem/plano.md) aos destinos derivados: requisitos (`REQ-*`), decisões (`ADR-*`), planos de implementação (`PLN-*`) e pastas de especificação (`arquitetura/`, `dados/`, `modelos/`, `interface/`, `estrutura/`).

Regra de aceitação (ver [docs/LEITURA.md](../LEITURA.md)): **toda a secção do plano tem de ter destino**. Uma secção sem linha na matriz é um buraco — fecha-se antes de este PR ficar pronto. A secção [Buracos](matriz.md#buracos) em [matriz.md](matriz.md) tem de ficar vazia (ou declarar explicitamente que não há buracos).

## Como usar

1. Abre [matriz.md](matriz.md).
2. Na tabela principal, encontra a secção do plano (títulos `##` de `plano.md`, mais a introdução sem `##`).
3. Segue os IDs `REQ-*` / `ADR-*` / `PLN-*` e os caminhos de docs relacionados.
4. Para o sentido inverso (área de requisito → secções do plano), usa o [índice inverso](matriz.md#índice-inverso-req--plano).

## Convenções

| Prefixo | Significado | Fonte |
| --- | --- | --- |
| `REQ-AAA-NNN` | Requisito numerado | [docs/requisitos/](../requisitos/) |
| `ADR-NNN` | Decisão de arquitectura | [docs/decisoes/](../decisoes/) |
| `PLN-NN` | Plano de implementação | [docs/planos/](../planos/) (ordem `PLN-01` … `PLN-21`) |

- Português de Portugal.
- A matriz **não** reescreve o plano: só aponta.
- IDs de planos seguem a ordem acordada mesmo se o ramo `docs/planos` ainda não estiver no remoto.
- Em conflito de intenção, `docs/origem/plano.md` e as decisões de fecho em `docs/LEITURA.md` ganham.

## Ordem de leitura sugerida

1. `docs/origem/plano.md`
2. `docs/LEITURA.md`
3. Esta pasta → [matriz.md](matriz.md)
4. Destinos (`requisitos/`, `decisoes/`, `planos/`, …) conforme a linha da matriz
