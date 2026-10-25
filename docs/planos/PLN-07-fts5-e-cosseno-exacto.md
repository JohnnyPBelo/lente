# PLN-07: FTS5 e cosseno exacto (sqlite-vec)

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Ligar FTS5 e sqlite-vec no mesmo ficheiro SQLite; pesquisa lexical + varrimento de cosseno exacto 256d (sem índice aproximado); devolver candidatos unidos sem ainda fundir RRF nem juiz.
**Fronteira:** o que NÃO entra neste plano — RRF/Platt (PLN-09), juiz (PLN-08), Qdrant/Chroma/LanceDB/Postgres, extensão Vec1 oficial do SQLite se for ANN.
**Ficheiros futuros:**
- `engine/pesquisa/__init__.py`
- `engine/pesquisa/fts.py` — popular e consultar FTS5
- `engine/pesquisa/vec.py` — carregar extensão sqlite-vec; insert/query cosseno
- `engine/pesquisa/candidatos.py` — união embedding ∪ FTS (sem RRF ainda)
- `engine/armazenamento/esquema/002_fts_vec.sql` (se não estiver no 001)
- `tests/pesquisa/test_fts5.py`
- `tests/pesquisa/test_cosseno_exacto.py`
**Teste que falha primeiro:** `tests/pesquisa/test_cosseno_exacto.py` — inserir 3 vectores conhecidos; consulta com o vector idêntico ao #2 devolve `#2` em primeiro com score cosseno ≈ 1.0; nenhum vizinho omitido numa base de N pequenos.

## Passos

- [ ] Teste FTS: indexar blocos com termo raro `CVE-2099-0001`; query FTS devolve esse bloco.
- [ ] Teste cosseno exacto (acima).
- [ ] Commit: `test(pesquisa): falha sem FTS5 e sqlite-vec`.
- [ ] Migração: tabela virtual FTS5 + tabela/vec sqlite-vec 256d.
- [ ] Carregar extensão no `ligacao.py` (caminho da `.so`/`.dll` documentado).
- [ ] Popular FTS na indexação; manter sincronizado em delete/reindex.
- [ ] Query cosseno: varrimento exacto; ordenar por similaridade.
- [ ] `candidatos.py`: merge por id de frase/bloco sem scores RRF.
- [ ] Fazer passar.
- [ ] Commit: `feat(pesquisa): FTS5 e cosseno exacto sqlite-vec`.
- [ ] Teste: identificador literal (sigla/CVE) aparece nos candidatos FTS mesmo com embedding fraco (fixture).
- [ ] Teste de regressão documentado: **não** usar ANN / Vec1 aproximado.
- [ ] Commit: `test(pesquisa): literais FTS e anti-ANN`.
- [ ] Commit de fecho.

## Notas para o executor

- Escala alvo: milhares de documentos; se deixar de caber em ms, manter exactidão (ADR-015).
- Um ficheiro SQLite = documentos + FTS + vectores + chats.
