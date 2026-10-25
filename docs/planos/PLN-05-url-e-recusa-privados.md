# PLN-05: URL e recusa de endereços privados

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Importar artigo via URL HTTP(S): descarregar, extrair texto principal, registar como documento; **recusar** endereços privados, loopback, link-local e esquemas não HTTP(S).
**Fronteira:** o que NÃO entra neste plano — browser automation, login em sites, sync cloud, PDF remoto complexo além do fluxo já coberto por extractores; UI do estado «URL recusada» (copy em PLN-21).
**Ficheiros futuros:**
- `engine/ingestao/url.py` — fetch + extracção
- `engine/ingestao/ssrf.py` — validação de host/IP (bloqueio privado)
- `tests/ingestao/test_ssrf.py`
- `tests/ingestao/test_url.py`
**Teste que falha primeiro:** `tests/ingestao/test_ssrf.py` — `validar_url("http://127.0.0.1/x")` e `http://192.168.0.1/`, `http://10.0.0.1/`, `http://[::1]/`, `file:///etc/passwd` levantam `UrlRecusada`; um host público de teste (mock DNS/IP) passa a validação estática.

## Passos

- [ ] Escrever matriz de casos SSRF (RFC1918, loopback, link-local, metadata cloud `169.254.169.254`, DNS rebinding: resolver e voltar a verificar IP).
- [ ] Testes que falham para `ssrf.py`.
- [ ] Commit: `test(ingestao): falha sem recusa de URLs privadas`.
- [ ] Implementar validação: só `http`/`https`; rejeitar credenciais no URL se política assim o disser; resolver DNS e bloquear se qualquer A/AAAA for privado.
- [ ] Implementar fetch com timeout, limite de tamanho, User-Agent identificável «Lente».
- [ ] Extrair texto (ex. readability / trafilatura / html.parser) → mesmo pipeline de registo.
- [ ] Testes de URL com servidor HTTP local de fixture **só** se o validador tiver modo de teste explícito; caso contrário mockar resposta após validação.
- [ ] Fazer passar.
- [ ] Commit: `feat(ingestao): URL com bloqueio SSRF`.
- [ ] Teste: redirect para IP privado a meio do caminho → recusa.
- [ ] Commit: `test(ingestao): redirects maliciosos recusados`.
- [ ] Commit de fecho.

## Notas para o executor

- Mensagem de erro estável para a UI: código `url_recusada` (estado vazio PLN-21).
- Sem contas nem rede persistente além do fetch pontual pedido pelo utilizador.
