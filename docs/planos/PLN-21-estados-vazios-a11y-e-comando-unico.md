# PLN-21: Estados vazios, acessibilidade e comando único

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Cobrir estados vazios observáveis (biblioteca sem ficheiros, modelo a descarregar, prosa toda filtrada, página sem texto, URL recusada, conversa nova, procura sem documentos); acessibilidade (foco, teclado, rótulos, `prefers-reduced-motion` já exigido); um comando sobe UI+motor em `127.0.0.1:4317`; piso Python 3.11+ / Node 22 / 16 GB documentado; se HF bloquear download, a app abre e diz onde pôr o ficheiro.
**Fronteira:** o que NÃO entra neste plano — novas funcionalidades de produto; Electron; segundo modo GPU.
**Ficheiros futuros:**
- `apps/ui/src/components/vazios/BibliotecaVazia.tsx`
- `apps/ui/src/components/vazios/ModeloADescarregar.tsx`
- `apps/ui/src/components/vazios/ProsaFiltrada.tsx`
- `apps/ui/src/components/vazios/PaginaSemTexto.tsx`
- `apps/ui/src/components/vazios/UrlRecusada.tsx`
- `apps/ui/src/components/vazios/ConversaNova.tsx`
- `apps/ui/src/components/vazios/ProcuraSemDocumentos.tsx`
- `apps/ui/src/a11y/focos.ts` / checklist em testes
- `engine/runtime/pesos.py` — resolver caminhos; mensagens se em falta
- `scripts/lente` ou `pyproject.toml` entrypoint `lente`
- `README.md` (raiz) — secção «Como correr» actualizada quando o código existir
- `tests/runtime/test_comando_unico.py`
- `tests/ui/a11y/estados-vazios.test.tsx`
**Teste que falha primeiro:** `tests/runtime/test_comando_unico.py` — invocar o entrypoint em processo (ou módulo `engine.cli:main`) com porto de teste; após ready, `GET http://127.0.0.1:<porto>/` devolve 200 (UI ou placeholder); existe **um** listener na interface de loopback; com pesos E2B ausentes, o processo **não** termina — endpoint de saúde reporta `e2b: ausente` e procura ainda devolve excertos.

## Passos

- [ ] Mapear cada estado vazio → componente + copy PT (ver `docs/interface/estados-vazios.md` / `copy.md` quando no main).
- [ ] Testes de render: cada vazio mostra texto distintivo e CTA quando aplicável.
- [ ] Commit: `test(ui): falha sem estados vazios`.
- [ ] Implementar componentes e ligação aos códigos de erro da API.
- [ ] Auditoria a11y: tab order na barra/modos/leitor; `aria-*` nos menus; contraste do vidro sobre fundo.
- [ ] Entrypoint único: aplicar migrações, ligar modelos residentes, servir UI, bind `127.0.0.1`.
- [ ] Mensagens se EmbeddingGemma/juiz/E2B em falta: abrir app + instruções de caminho.
- [ ] Fazer passar testes runtime + UI.
- [ ] Commit: `feat: estados vazios, a11y e comando único lente`.
- [ ] Teste manual documentado no plano (checklist): Windows/macOS/Linux smoke; 16 GB; com e sem GPU.
- [ ] Checklist final: nenhum trabalho pesado paralelo; sem bind público; Tesseract único dep de sistema.
- [ ] Commit de fecho: `chore: PLN-21 concluído — app arranca num comando`.

## Checklist de aceitação global (smoke)

- [ ] `lente` (ou equivalente) escuta só `127.0.0.1:4317`.
- [ ] Biblioteca vazia mostra estado, não erro genérico.
- [ ] URL privada → `UrlRecusada`.
- [ ] Procura sob limiar → aviso sem documentos/miniaturas falsas.
- [ ] Prosa filtrada toda → excertos ou vazio, sem prosa fantasma.
- [ ] `prefers-reduced-motion` não remove leque/leitor.
- [ ] Backup zip e dossier export ainda funcionam sem rede.

## Notas para o executor

- Este plano fecha a vertical de produto mínima descrita em `docs/origem/plano.md` «Como corre» e «Estados vazios».
- Fora de âmbito permanece: bases vectoriais separadas, ANN, Jev, fine-tune E2B, contas, áudio, visão encoder, procedimentos de ataque.
