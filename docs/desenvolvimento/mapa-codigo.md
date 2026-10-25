# Mapa de código

[docs/estrutura/arvore.md](../estrutura/arvore.md) nomeia papéis (`indice`, `escritor`). [docs/planos/](../planos/) nomeia os pacotes que se criam. Este mapa é o que o desenvolvimento segue. Os IDs `MOD-…` continuam a ser os contratos em [docs/estrutura/modulos.md](../estrutura/modulos.md).

| Pacote | Plano | Papel na árvore | Contrato |
| --- | --- | --- | --- |
| `engine/armazenamento/` | PLN-01, migração 002 no PLN-07 | armazenamento | esquema em `docs/dados/esquema.md` |
| `engine/ingestao/` | PLN-02 … PLN-05 | ingestão | MOD-ingestao |
| `engine/embeddings/` | PLN-06 | índice (vectores) | MOD-emb |
| `engine/pesquisa/` | PLN-07, PLN-09 | pesquisa | MOD-pesquisa |
| `engine/juiz/` | PLN-08 | juiz | MOD-juiz |
| `engine/escalonador/` | PLN-10 | escalonador | MOD-escalonador |
| `engine/resposta/` | PLN-11 | escritor | MOD-escritor |
| `engine/api/` | PLN-12, rotas que os planos seguintes acrescentam | api | `docs/estrutura/contrato-http.md` |
| `apps/ui/` | PLN-13 … PLN-15, PLN-21 | ui | `docs/interface/` |
| `engine/feedback/` | PLN-16, PLN-17 | juiz (afinação) | MOD-juiz, `docs/dados/correcoes.schema.json` |
| `engine/dossier/` | PLN-18 | armazenamento (fotografia) | `docs/dados/dossier.schema.json` |
| `engine/alertas/` | PLN-19 | pesquisa + juiz, sem E2B | MOD-pesquisa |
| `engine/diario/`, `engine/biblioteca/`, `engine/backup/` | PLN-20 | armazenamento | MOD-armazenamento |
| `engine/runtime/`, `scripts/lente` ou entrypoint `lente` | PLN-21 | processo único | ADR-013 |

Não criar `engine/indice/` nem `engine/escritor/` como pacotes paralelos. A indexação vive em `engine/embeddings/indexar.py` mais o repositório. A prosa vive em `engine/resposta/`.

## Testes

| Código | Teste |
| --- | --- |
| `engine/<pacote>/` | `tests/<pacote>/` |
| `apps/ui/src/` | `apps/ui` com Vitest, ficheiros `*.test.tsx` ao lado ou em `apps/ui/src` conforme o plano |

O primeiro teste de cada plano está na secção «Teste que falha primeiro» desse PLN. Escreve-se antes da implementação.

## UI

React, shadcn/ui reestilizado, Geist no chrome, serif na superfície do leitor. Copy em [docs/interface/copy.md](../interface/copy.md). O cliente HTTP fala só com `127.0.0.1`. O artefacto de `apps/ui` é estático; o motor monta-o.

## Entrypoint

O nome do comando é `lente`. Faz três coisas, por esta ordem: aplica migrações, sobe o que estiver em `models/` (e regista o que falta), escuta em `127.0.0.1:4317`. Node não fica nesse processo.
