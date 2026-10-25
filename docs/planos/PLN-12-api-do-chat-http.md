# PLN-12: API do chat (HTTP)

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Servidor HTTP único em `127.0.0.1:4317` (Python) com endpoints do chat/procura, conversas CRUD mínimo, e servir estáticos quando existirem; liga escalonador + pipeline de pesquisa + resposta.
**Fronteira:** o que NÃO entra neste plano — chrome React completo (PLN-13+), Electron, segundo servidor Node em runtime.
**Ficheiros futuros:**
- `engine/api/__init__.py`
- `engine/api/app.py` — ASGI/WSGI app
- `engine/api/rotas_chat.py` — conversas, mensagens, procura
- `engine/api/rotas_biblioteca.py` — listar/enfileirar documentos (mínimo)
- `engine/api/erros.py` — códigos estáveis (`url_recusada`, `fila_ocupada`, `limiar_vazio`, …)
- `engine/api/estaticos.py` — montar `apps/ui/dist` se presente
- `tests/api/test_chat_procurar.py`
- `tests/api/test_bind.py`
**Teste que falha primeiro:** `tests/api/test_chat_procurar.py` — `POST /api/conversas/{id}/procurar` com corpo `{ "texto": "…", "modo": "procurar", "lente": "investigar" }` devolve 200 JSON com `excertos` ou `aviso_vazio`, nunca prosa sem lista `frases` já filtrada; com fixture indexada mínima, inclui `citacoes[].documento_id` e offsets.

## Passos

- [ ] Escolher framework (ex. Starlette/FastAPI) e cliente de teste.
- [ ] Teste bind: listener só em `127.0.0.1:4317` (não `0.0.0.0`).
- [ ] Commit: `test(api): falha sem procura HTTP local`.
- [ ] Implementar CRUD conversas: criar, listar, renomear, apagar; primeira procura pode nomear.
- [ ] Endpoint procurar: adquire slot; corre pipeline; grava mensagens/citações.
- [ ] Streaming opcional: se streaming, miniaturas/excertos primeiro; prosa só após portas.
- [ ] Erros tipados → HTTP 4xx com `codigo`.
- [ ] Fazer passar com BD tmp e modelos mock.
- [ ] Commit: `feat(api): chat e procura em 127.0.0.1:4317`.
- [ ] Teste: sem E2B → 200 com excertos.
- [ ] Teste: CORS desnecessário em same-origin; não expor bind público.
- [ ] Commit: `test(api): degradação sem E2B e bind local`.
- [ ] Commit de fecho.

## Notas para o executor

- Node 22 só no build da UI; runtime = um processo Python.
- Contratos HTTP futuros alinhados a `HTTP-search` etc. quando `docs/estrutura/` existir.
