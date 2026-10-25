# PLN-10: Escalonador (um trabalho pesado)

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Garantir um trabalho pesado de cada vez: procura pausa indexação e LoRA e retoma-os no fim; reservar ≥2 núcleos para sistema/UI; limitar E2B a `nproc-2` e LoRA a 2 núcleos.
**Fronteira:** o que NÃO entra neste plano — HTTP completo (PLN-12), UI de estados do escalonador (telemetria mínima ok), treino LoRA real (ganchos + stub).
**Ficheiros futuros:**
- `engine/escalonador/__init__.py`
- `engine/escalonador/slot.py` — mutex/async lock do slot pesado
- `engine/escalonador/estados.py` — `idle|search|index|lora|paused_for_search`
- `engine/escalonador/nucleos.py` — cálculo de limites CPU
- `engine/escalonador/fila_ingestao.py` — um documento de cada vez
- `tests/escalonador/test_slot.py`
- `tests/escalonador/test_nucleos.py`
**Teste que falha primeiro:** `tests/escalonador/test_slot.py` — com indexação «em curso» (tarefa async/thread controlada), ao adquirir slot `search` a indexação observa pausa; após libertar search, a indexação retoma e conclui; nunca dois `search` em paralelo.

## Passos

- [ ] Escrever teste de pausa/retoma com relógios/eventos determinísticos.
- [ ] Commit: `test(escalonador): falha sem slot único`.
- [ ] Implementar slot + estados observáveis (`estado_atual()`).
- [ ] `nucleos.py`: tabelas 4/8/16 núcleos como na arquitectura.
- [ ] Fila de ingestão: um documento; API `enfileirar` / `proximo`.
- [ ] Integração fina: hooks `antes_de_indexar`, `antes_de_procurar`, `antes_de_lora`.
- [ ] Recusar segundo pesado com erro tipado `FilaOcupada` (mensagem estável).
- [ ] Fazer passar.
- [ ] Commit: `feat(escalonador): um trabalho pesado e limites de CPU`.
- [ ] Teste: feedback imediato em disco **não** pede slot pesado.
- [ ] Teste: procura usa ONNX activo mesmo se LoRA estiver pausado a meio.
- [ ] Commit: `test(escalonador): leves vs pesados`.
- [ ] Commit de fecho.

## Notas para o executor

- Trabalhos pesados: procura (incl. correlacionar/lacunas), indexação, E2B dentro da procura, LoRA.
- GPU acelera o mesmo caminho; não há segundo modo.
