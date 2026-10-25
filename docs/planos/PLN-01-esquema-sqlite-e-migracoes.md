# PLN-01: Esquema SQLite e migrações

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Criar a camada de armazenamento local: ficheiro SQLite em `data/`, esquema inicial alinhado a `docs/dados/esquema.md` (quando existir no ramo principal) e motor de migrações versionadas, sem modelos nem HTTP.
**Fronteira:** o que NÃO entra neste plano — ingestão de ficheiros, embeddings, FTS5/sqlite-vec além do schema mínimo necessário para as tabelas, API, UI, juiz, E2B.
**Ficheiros futuros:**
- `engine/armazenamento/__init__.py`
- `engine/armazenamento/caminho.py` — resolve `data/` e o nome do ficheiro `.sqlite`
- `engine/armazenamento/ligacao.py` — abre ligação, PRAGMA (FK, WAL)
- `engine/armazenamento/migracoes.py` — aplica migrações em ordem
- `engine/armazenamento/esquema/001_inicial.sql` — tabelas base (documentos, hashes, blocos, frases, conversas, mensagens, fila, versoes_modelo, …)
- `engine/armazenamento/repositorio.py` — helpers mínimos (abrir, estado do esquema)
- `tests/armazenamento/test_migracoes.py`
- `tests/armazenamento/conftest.py` — tmp `data/` por teste
**Teste que falha primeiro:** `tests/armazenamento/test_migracoes.py` — após `aplicar_migracoes(caminho_tmp)`, `PRAGMA user_version` ≥ 1 e existem as tabelas `documentos`, `documento_hashes`, `blocos`, `frases` (consulta a `sqlite_master`).

## Passos

- [ ] Criar pacote `engine/armazenamento/` vazio e `tests/armazenamento/`.
- [ ] Escrever o teste que falha: ficheiro temporário, `aplicar_migracoes`, assert tabelas + `user_version`.
- [ ] Commit: `test(armazenamento): falha sem migrações SQLite`.
- [ ] Implementar `caminho.py`: raiz do projecto → `data/`; criar pasta se não existir; caminho do DB documentado.
- [ ] Implementar `ligacao.py`: `sqlite3.connect`, `PRAGMA foreign_keys=ON`, `journal_mode=WAL`, tipagem explícita.
- [ ] Escrever `001_inicial.sql` com as tabelas do núcleo (documentos, documento_hashes, blocos, frases, fila, conversas, mensagens, citacoes, trechos_fixados, feedback, dossiers, alertas, diario, etiquetas, documento_etiquetas, versoes_modelo) e índices nomeados `idx_…`.
- [ ] Implementar `migracoes.py`: listar SQL ordenados; transação; actualizar `user_version`; idempotente se já aplicado.
- [ ] Fazer o teste passar.
- [ ] Commit: `feat(armazenamento): migração 001 e ligação SQLite`.
- [ ] Teste: reabrir a mesma BD não recria tabelas nem falha; segunda chamada a `aplicar_migracoes` é no-op.
- [ ] Teste: `FOREIGN KEY` activa — inserir `bloco` com `documento_id` inexistente falha.
- [ ] Teste: `documentos.estado` só aceita `ok|desactualizado|a_indexar|erro` (CHECK).
- [ ] Commit: `test(armazenamento): FK e CHECK do esquema inicial`.
- [ ] Documentar no docstring do pacote: um ficheiro SQLite leva documentos, FTS, chats, feedback e dossiers; cópia do ficheiro = cópia do índice.
- [ ] Commit final do plano: `docs(armazenamento): PLN-01 concluído` (ou mensagem equivalente se só houver código).

## Notas para o executor

- Datas em ISO-8601 UTC (`TEXT`). Booleanos `INTEGER` 0/1.
- Não ligar ainda `sqlite-vec` nem criar tabela virtual FTS aqui além de placeholders se o SQL 001 os exigir; se o esquema de dados exigir FTS/vec no 001, criar só a estrutura e deixar a lógica de pesquisa para PLN-07.
- Referência: `docs/origem/plano.md` (Base vectorial, Entradas) e ADR-002 quando existir no ramo.
