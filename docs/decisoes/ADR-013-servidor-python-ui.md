# ADR-013 — Um só servidor Python serve a UI

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

É preciso um único comando que suba motor e interface em desktop (Windows, macOS, Linux), sem empacotar um browser Chromium completo nem manter dois servidores em desenvolvimento e produção.

## Decisão

**Um só servidor Python** escuta em `127.0.0.1:4317` e **serve a UI já construída**. **Node 22** serve **só para o build** da interface. **Sem Electron.**

Piso: Python 3.11+, Node 22, 16 GB de RAM.

## Consequências

- Distribuição e runtime simplificados: um processo, um porto.
- Node não é dependência de runtime do utilizador final após o build.
- Sem shell Electron: menos superfície e menos RAM; o browser do sistema abre localhost.

## Alternativas rejeitadas

- Electron ou Tauri como contentor obrigatório.
- Servidor Node separado a servir a UI em produção.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secção «Como corre»; fecho em [docs/LEITURA.md](../LEITURA.md).
