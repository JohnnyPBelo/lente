# PLN-15: Leque e leitor

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Após resposta com documentos: miniaturas; um doc abre leitor; vários abrem leque → escolha → cresce até leitor; Escape/minimizar recolhe; leitor com scroll contínuo, highlights literais, zoom, sumário, cópia de citação, fixar trecho; serif no texto; `prefers-reduced-motion` encurta sem remover leque/leitor.
**Fronteira:** o que NÃO entra neste plano — dossier (PLN-18), feedback LoRA (PLN-16), OCR novo.
**Ficheiros futuros:**
- `apps/ui/src/components/leque/Leque.tsx`
- `apps/ui/src/components/leque/Miniatura.tsx`
- `apps/ui/src/components/leitor/Leitor.tsx`
- `apps/ui/src/components/leitor/Highlights.tsx`
- `apps/ui/src/components/leitor/Sumario.tsx`
- `apps/ui/src/components/leitor/Ferramentas.tsx` — zoom, página, procurar neste doc
- `apps/ui/src/components/chat/CitacaoLink.tsx` — clique → leitor na página/highlight
- `engine/api/rotas_documento.py` — bytes/páginas/sumário/miniatura
- `tests` UI: `Leque.test.tsx`, `Leitor.highlights.test.tsx`
**Teste que falha primeiro:** `Leque.test.tsx` — com 3 miniaturas, hover/foco (desktop) revela leque; click na 2.ª chama `onAbrir(docId)`; com `prefers-reduced-motion: reduce`, animações curtas/ausentes mas leque e abertura permanecem disponíveis.

## Passos

- [ ] Teste do leque (acima) + teste: 1 documento salta o leque.
- [ ] Commit: `test(ui): falha sem leque de miniaturas`.
- [ ] Implementar miniaturas a partir de URLs da API; tacto: 1.º toque leque, 2.º abre.
- [ ] Leitor: PDF/texto/md/URL/imagem; highlights por offsets/caixas; salto entre marcas.
- [ ] Citação no chat abre leitor directo (sem obrigar leque).
- [ ] Seleccionar → copiar; copiar citação com ficheiro+página; fixar trecho → API linha SQLite.
- [ ] Bolha «Confrontar» com selecção preenche lugar vazio (liga PLN-14).
- [ ] Corrigir highlight (selecção) — API de feedback parcial ok; treino em PLN-16.
- [ ] Fazer passar.
- [ ] Commit: `feat(ui): leque e leitor com prova na página`.
- [ ] Teste: highlight é intervalo literal do ficheiro (fixture controlada).
- [ ] Commit: `test(ui): highlight literal e reduced-motion`.
- [ ] Commit de fecho.

## Notas para o executor

- Miniaturas feitas na indexação, não render PDF no hover.
- Superfície de texto sólida com serif; chrome continua em vidro.
