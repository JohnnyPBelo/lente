# ADR-002 — SQLite único com FTS5 e sqlite-vec

**Estado:** Aceite  
**Data:** 2026-10-25

## Contexto

É preciso guardar documentos, texto exacto, vectores, chats, feedback e dossiers, com pesquisa semântica e literal, sem segundo processo nem base externa.

## Decisão

Um único ficheiro SQLite em `data/`, com FTS5 e a extensão `sqlite-vec` no mesmo processo. Os vectores vivem no mesmo ficheiro que o resto. A pesquisa semântica é **cosseno exacto**, não aproximada. Texto exacto e semântica fundem-se por rank recíproco; o juiz filtra o que se marca.

## Consequências

- Uma cópia do ficheiro leva o índice consigo; sobrevive a reinícios.
- Sem outro processo de base vectorial; menos memória e menos superfície de falha.
- O cosseno exacto não omite vizinhos; a escala alvo é milhares de documentos com vectores de 256 dimensões (ver [ADR-015](ADR-015-escala-cosseno-exacto.md)).

## Alternativas rejeitadas

- **Vec1** (extensão oficial SQLite) — ainda pré-1.0 e índice aproximado; pode omitir o trecho certo.
- **Qdrant, Chroma, LanceDB, Postgres** — outro processo e mais memória.

## Apontador

[docs/origem/plano.md](../origem/plano.md) — secção «Base vectorial».
