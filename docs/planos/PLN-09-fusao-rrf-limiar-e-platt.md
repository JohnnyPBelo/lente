# PLN-09: Fusão RRF, limiar e Platt

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Fundir rankings FTS e embedding por Reciprocal Rank Fusion; aplicar limiar visível do juiz; com correções suficientes, calibrar scores com escala de Platt nos exemplos do utilizador; privilegio imediato a trechos confirmados/rejeitados sem injectar texto no escritor.
**Fronteira:** o que NÃO entra neste plano — treino LoRA (PLN-16), escrita E2B, UI do limiar (pode expor valor na API).
**Ficheiros futuros:**
- `engine/pesquisa/rrf.py`
- `engine/pesquisa/limiar.py`
- `engine/pesquisa/platt.py`
- `engine/pesquisa/pipeline.py` — candidatos → RRF → juiz → filtro limiar
- `engine/pesquisa/feedback_runtime.py` — boost/penalização por feedback recente
- `tests/pesquisa/test_rrf.py`
- `tests/pesquisa/test_limiar_platt.py`
**Teste que falha primeiro:** `tests/pesquisa/test_rrf.py` — dados duas listas ordenadas com ids sobrepostos, `rrf(a, b, k=60)` coloca no topo um id que está bem ranqueado em ambas; ids só numa lista ficam abaixo desse consenso.

## Passos

- [ ] Implementar testes RRF com k configurável (default 60).
- [ ] Commit: `test(pesquisa): falha sem fusão RRF`.
- [ ] Implementar `rrf.py` puro (sem I/O).
- [ ] `pipeline.py`: embedding query com prefixo da lente (defaults até PLN-14); FTS; RRF; juiz; limiar.
- [ ] Limiar default documentado e **lido** de config/BD (visível).
- [ ] Platt: só se N correções ≥ limiar mínimo documentado; senão identity.
- [ ] Feedback runtime: pergunta muito parecida privilegia positivos e desce rejeitados **entre candidatos já recuperados**.
- [ ] Identificador literal: fura chão de cosseno; continua sujeito ao juiz (ADR-014).
- [ ] Testes unitários para limiar (abaixo → vazio) e Platt (monotonicidade em fixture).
- [ ] Commit: `feat(pesquisa): RRF, limiar e Platt`.
- [ ] Teste: procura sem nada acima do limiar → lista vazia de highlights (aviso de vazio na API/UI depois).
- [ ] Commit: `test(pesquisa): limiar vazio e literais`.
- [ ] Commit de fecho.

## Notas para o executor

- Prefixos de query por lente: ver LEITURA.md / ADR-009; stubs aceitáveis até PLN-14 ligar a barra.
- Não injectar texto de feedback no E2B.
