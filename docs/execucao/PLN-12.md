# Ordem de trabalho PLN-12

Fonte: `docs/planos/PLN-12-api-do-chat-http.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Servidor HTTP único em `127.0.0.1:4317` (Python) com endpoints do chat/procura, conversas CRUD mínimo, e servir estáticos quando existirem; liga escalonador + pipeline de pesquisa + resposta.

## Fronteira

o que NÃO entra neste plano — chrome React completo (PLN-13+), Electron, segundo servidor Node em runtime.

## Teste que falha primeiro, no plano

`tests/api/test_chat_procurar.py` — `POST /api/conversas/{id}/procurar` com corpo `{ "texto": "…", "modo": "procurar", "lente": "investigar" }` devolve 200 JSON com `excertos` ou `aviso_vazio`, nunca prosa sem lista `frases` já filtrada; com fixture indexada mínima, inclui `citacoes[].documento_id` e offsets.

Nesta ordem esse teste é `test_reg_http_001`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-09
- PLN-10
- PLN-11

## Ficheiros que este PR pode criar

- `engine/api/__init__.py`
- `engine/api/app.py` — ASGI/WSGI app
- `engine/api/rotas_chat.py` — conversas, mensagens, procura
- `engine/api/rotas_biblioteca.py` — listar/enfileirar documentos (mínimo)
- `engine/api/erros.py` — códigos estáveis (`url_recusada`, `fila_ocupada`, `limiar_vazio`, …)
- `engine/api/estaticos.py` — montar `apps/ui/dist` se presente
- `tests/api/test_chat_procurar.py`
- `tests/api/test_bind.py`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- apps/ui/ (PLN-13 em diante), Electron, um segundo servidor Node
- engine/api/rotas_modos.py (PLN-14), rotas_documento.py (PLN-15)
- rotas de dossier, alertas, correcções, backup e modelos, que entram nos planos donos

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

O contrato já está em docs/estrutura/contrato-http.md. O procurar é POST /search, com chat_id, texto e lente, resposta text/event-stream: miniaturas, excerto, frase só depois das portas, vazio, fim. Não usar o caminho /api/conversas/.../procurar do rascunho antigo do plano. Erros são {erro, mensagem}. Este PR cria HTTP-health, HTTP-search, HTTP-chat-list, HTTP-chat-create, HTTP-chat-get, HTTP-chat-rename e HTTP-chat-delete. Os outros endpoints ficam nos planos donos. Testes com base temporária e modelos em double. Não escutar em 0.0.0.0.

## Requisitos que este PR fecha

- `REQ-CHT-002` fecha com `REG-CHT-002`.
- `REQ-SEG-002` fecha com `REG-SEG-002`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/api/test_chat_nome.py::test_reg_cht_002`
  - Dado uma conversa sem nome escolhido pelo utilizador, quando entra a primeira procura, então o título passa a derivar desse texto.
- `tests/api/test_bind.py::test_reg_seg_002`
  - Dado o servidor por omissão, quando se inspecciona o bind, então o host é 127.0.0.1 e o porto de serviço sem argumentos é 4317. Configurar 0.0.0.0 falha. O teste usa um porto livre de loopback e não abre a rede.
- `tests/api/test_chat_procurar.py::test_reg_http_001`
  - Dado uma fixture mínima e modelos em double, quando se faz POST /search com chat_id, texto e lente investigar, então a resposta é 200 em text/event-stream, traz excerto com documento_id e offsets ou o evento vazio, e não emite frase sem a lista já filtrada. Sem E2B continua 200 com excertos. O teste não abre 0.0.0.0 nem descarrega pesos.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] O texto visível vem de `docs/interface/copy.md`, sem frase inventada para o mesmo estado.

## Paralelo

Pode avançar ao lado de PLN-13, que usa respostas falsas, e dos planos que não escrevem em engine/api/. PLN-14 e PLN-15 acrescentam rotas em ficheiros novos, com rebase se app.py for o único ponto de registo.
