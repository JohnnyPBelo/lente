# ADR-014 — Identificador literal fura o chão de cosseno

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

CVE, números de cláusula, siglas e códigos escritos à letra têm semelhança de embedding média mesmo quando são a resposta certa. Um limiar de cosseno cego descartá-los-ia.

## Decisão

FTS5 no mesmo SQLite apanha o termo exacto. Os candidatos literais juntam-se aos do embedding (fusão por rank recíproco). Um **identificador literal fura o chão de cosseno** (entra nos candidatos mesmo com semelhança semântica média) mas **continua sujeito ao juiz** antes do highlight.

## Consequências

- Códigos e referências exactas não desaparecem só por cosseno baixo.
- O juiz continua a ser quem deixa passar a marca; não há highlight automático só por FTS.
- Implementação do limiar tem excepções explícitas para hits literais.

## Alternativas rejeitadas

- Só embedding, sem FTS.
- Marcar highlight só porque o FTS acertou, sem o juiz.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secção «Pesquisa, sem modelo a mais»; fecho em [docs/LEITURA.md](../LEITURA.md).
