# ADR-008 — Superfície local sem contas nem sync

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

O Lente é uma app de secretária para prova local. Contas, permissões e sincronização em rede mudariam o modelo de ameaça e o âmbito do produto.

## Decisão

Superfície estritamente local: **sem contas**, **sem rede de sync**. O servidor escuta só em **127.0.0.1:4317**. Diário local só de acrescentar. Cópia de segurança = pasta `data/` num zip escolhido pelo utilizador, sem nuvem. URLs de artigos recusam endereços privados.

## Consequências

- Sem login, partilha automática ou multi-dispositivo.
- Exportar correcções / dossiers é ficheiro explícito, não sync.
- O binding a localhost é requisito de segurança da superfície ([ADR-013](ADR-013-servidor-python-ui.md)).

## Alternativas rejeitadas

- Contas, permissões e sincronização em nuvem.
- Escutar em `0.0.0.0` ou porta pública.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secções «Mais, ainda sem peso», «Como corre» e «De fora, porque pesa ou muda o modelo».
