# PLN-14: Barra de modos e lentes

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Barra de escrita única: menu `+` e `/` (setas, Enter, Escape); modos Procurar, Correlacionar, Confrontar, Alerta, Lacunas; pastilha de lente (investigar, assessment, acreditação, verificar); modo activo visível; sem páginas novas.
**Fronteira:** o que NÃO entra neste plano — leque/leitor (PLN-15), implementação completa de alertas backend (PLN-19), export/import de correcções (fica no estado da aprendizagem na lateral, PLN-17).
**Ficheiros futuros:**
- `apps/ui/src/components/barra/BarraEscrita.tsx`
- `apps/ui/src/components/barra/MenuMais.tsx`
- `apps/ui/src/components/barra/PastilhaModo.tsx`
- `apps/ui/src/components/barra/PastilhaLente.tsx`
- `apps/ui/src/components/barra/modos/Procurar.tsx`
- `apps/ui/src/components/barra/modos/Correlacionar.tsx`
- `apps/ui/src/components/barra/modos/Confrontar.tsx`
- `apps/ui/src/components/barra/modos/Alerta.tsx`
- `apps/ui/src/components/barra/modos/Lacunas.tsx`
- `apps/ui/src/lib/lentes.ts` — mapeamento lente → prefixo/instrução
- `engine/api/rotas_modos.py` — correlacionar, confrontar, lacunas (mínimo)
- `tests` UI: `BarraEscrita.test.tsx`; API: `tests/api/test_modos.py`
**Teste que falha primeiro:** `BarraEscrita.test.tsx` — pressionar `/` abre o menu; setas movem opção activa; Enter selecciona «Correlacionar» e a barra mostra dois campos «Conceito A» e «Conceito B»; Escape volta a Procurar de uma linha.

## Passos

- [ ] Teste de teclado do menu (acima).
- [ ] Commit: `test(ui): falha sem menu de modos na barra`.
- [ ] Implementar menu vidro por cima da barra; pastilhas de modo e lente.
- [ ] Correlacionar: dois campos; Enter envia ambos; API devolve cores A/B/relação (contrato).
- [ ] Confrontar: lugares Trecho A/B; escolha a partir de citações ou texto colado; três leituras determinísticas no motor (ADR-010).
- [ ] Alerta: placeholder «O que queres que eu vigie?»; limite 10 (validação API).
- [ ] Lacunas: textarea multilinha; Shift+Enter nova linha; Enter envia; sem E2B.
- [ ] Lente não altera Confrontar; altera prefixos de Procurar/Alerta/Lacunas.
- [ ] Fazer passar testes UI + API.
- [ ] Commit: `feat(ui+api): modos da barra e lentes`.
- [ ] Teste: bolha «Confrontar» no leitor pode ficar stub até PLN-15; documentar TODO se necessário.
- [ ] Commit de fecho.

## Notas para o executor

- Exportar/Importar correcções **não** entram neste menu.
- Lentes → prefixos EmbeddingGemma (LEITURA.md ponto 4).
