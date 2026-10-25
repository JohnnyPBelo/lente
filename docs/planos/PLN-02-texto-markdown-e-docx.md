# PLN-02: Texto, Markdown e docx

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Extrair texto e metadados mínimos de entradas `.txt`, Markdown e `.docx`, calcular SHA-256, e registar o documento na biblioteca com estado `a_indexar` ou `ok` conforme o fluxo de fila (sem embeddings ainda).
**Fronteira:** o que NÃO entra neste plano — PDF, OCR, URL, corte em blocos/embeddings, FTS, UI de importação (só API/função de motor se útil para testes).
**Ficheiros futuros:**
- `engine/ingestao/__init__.py`
- `engine/ingestao/hash.py` — SHA-256 dos bytes
- `engine/ingestao/tipos.py` — discriminar extensão / MIME
- `engine/ingestao/texto.py` — `.txt` (UTF-8 com fallbacks documentados)
- `engine/ingestao/markdown.py` — `.md` / `.markdown` → texto + títulos para sumário
- `engine/ingestao/docx.py` — `.docx` → texto plano por parágrafo
- `engine/ingestao/registo.py` — upsert em `documentos` + `documento_hashes` + enfileirar
- `tests/ingestao/test_hash.py`
- `tests/ingestao/test_texto_md_docx.py`
- `tests/fixtures/ingestao/amostra.txt`
- `tests/fixtures/ingestao/amostra.md`
- `tests/fixtures/ingestao/amostra.docx` (ficheiro mínimo sintético)
**Teste que falha primeiro:** `tests/ingestao/test_texto_md_docx.py` — `extrair("…/amostra.md")` devolve texto contendo um parágrafo conhecido e lista de títulos não vazia; `sha256_ficheiro` devolve hex de 64 chars estável.

## Passos

- [ ] Criar pacote `engine/ingestao/` e fixtures sintéticas (frases inventadas, sem texto de documentos reais).
- [ ] Escrever testes que falham para hash e extracção txt/md/docx.
- [ ] Commit: `test(ingestao): falha sem extractores txt/md/docx`.
- [ ] Implementar `hash.py`: leitura em blocos; hex minúsculo.
- [ ] Implementar extractores: normalizar newlines para `\n`; preservar ordem dos parágrafos no docx.
- [ ] Markdown: extrair headings (`#` …) para `sumario_json` preliminar (lista `{nivel, titulo, âncora?}`).
- [ ] `registo.py`: se caminho novo → inserir; se SHA mudou → `estado='desactualizado'` ou re-enfileirar conforme ADR/esquema; nunca servir índice antigo em silêncio.
- [ ] Fazer os testes passar.
- [ ] Commit: `feat(ingestao): texto, Markdown, docx e SHA-256`.
- [ ] Teste: ficheiro inexistente → erro tipado claro (não traceback genérico na API futura).
- [ ] Teste: dois ficheiros com o mesmo conteúdo → mesmo SHA; caminhos diferentes → dois `documentos`.
- [ ] Commit: `test(ingestao): erros e unicidade de caminho`.
- [ ] Garantir que a fila (`fila`) recebe no máximo a lógica de «um documento»; o processamento pesado fica para PLN-06/10.
- [ ] Commit de fecho do plano.

## Notas para o executor

- Dependência docx: biblioteca Apache-compatível (ex. `python-docx`); declarar em `pyproject.toml` quando existir.
- Encoding: tentar UTF-8; se falhar, documentar fallback (ex. latin-1) e teste com bytes não-UTF-8.
