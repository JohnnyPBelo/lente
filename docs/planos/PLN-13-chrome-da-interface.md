# PLN-13: Chrome da interface (apps/ui)

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Scaffold da UI em `apps/ui`: vidro líquido no chrome (fundo escuro neutro, blur, bordo de luz), Geist no chrome, layout com barra lateral de conversas e área de chat; PT; shadcn/ui reestilizado + motion curto; ainda sem barra de modos completa nem leitor.
**Fronteira:** o que NÃO entra neste plano — leque/leitor (PLN-15), modos/lentes completos (PLN-14), dossier/alertas UI.
**Ficheiros futuros:**
- `apps/ui/package.json` — Node 22
- `apps/ui/src/main.tsx`
- `apps/ui/src/App.tsx`
- `apps/ui/src/styles/tokens.css` — variáveis de cor/vidro (evitar roxo default AI)
- `apps/ui/src/components/chrome/BarraLateral.tsx`
- `apps/ui/src/components/chrome/AreaChat.tsx`
- `apps/ui/src/components/chrome/CampoEscritaBase.tsx` — campo + botão `+` stub
- `apps/ui/src/lib/api.ts` — cliente `127.0.0.1:4317`
- `apps/ui/src/components/chrome/Mensagem.tsx`
- `tests` ou Playwright/vitest: `apps/ui/src/components/chrome/BarraLateral.test.tsx`
**Teste que falha primeiro:** teste de componente/acessibilidade — `BarraLateral` renderiza botão «Nova conversa» e lista; com prop `conversas=[{id,nome}]` mostra o nome; contraste/rótulos em português (`Nova`, `Renomear`, `Apagar` via menu).

## Passos

- [ ] Scaffold Vite/React/TS; Geist; tokens CSS de vidro (blur, bordo luminoso, transparência).
- [ ] Escrever teste que falha da barra lateral.
- [ ] Commit: `test(ui): falha sem chrome da barra lateral`.
- [ ] Implementar barra lateral: conversas, nova, renomear, apagar (chama API).
- [ ] Área de chat: mensagens; tipografia chrome vs placeholder do leitor.
- [ ] Motion curto na entrada de mensagem (`prefers-reduced-motion` respeitado desde já).
- [ ] Build produz estáticos consumíveis por `engine/api/estaticos.py`.
- [ ] Fazer passar.
- [ ] Commit: `feat(ui): chrome vidro, lateral e chat base`.
- [ ] Teste visual/smoke: app serve index após build.
- [ ] Commit: `test(ui): build estático servido pelo motor`.
- [ ] Commit de fecho.

## Notas para o executor

- Copy em português (Portugal). Serif só no leitor (PLN-15).
- Não inventar dashboard: uma composição de chat.
