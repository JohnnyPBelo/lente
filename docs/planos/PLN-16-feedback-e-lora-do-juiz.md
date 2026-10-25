# PLN-16: Feedback e LoRA do juiz

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** UI e API de feedback (Acertou, Corrigir, Descartar) sem bloquear a procura seguinte; persistir pares; quando a máquina está livre, treinar LoRA rank 8 do juiz (≤2 núcleos), validar contra holdout, exportar ONNX novo e libertar PyTorch; procuras usam ONNX anterior até sucesso.
**Fronteira:** o que NÃO entra neste plano — import/export de ficheiro de correcções (PLN-17), fine-tune E2B, média de pesos LoRA de sítios diferentes.
**Ficheiros futuros:**
- `apps/ui/src/components/chat/FeedbackLinha.tsx`
- `engine/feedback/__init__.py`
- `engine/feedback/registar.py` — Acertou/Corrigir/Descartar
- `engine/feedback/lora.py` — treino rank 8, LR baixo, pull to base
- `engine/feedback/validar_troca.py` — rejeitar se holdout piorar
- `engine/feedback/exportar_onnx.py`
- `tests/feedback/test_registar.py`
- `tests/feedback/test_lora_gate.py`
**Teste que falha primeiro:** `tests/feedback/test_registar.py` — `Descartar` não cria pares de treino; `Acertou` marca trechos mostrados positivos; `Corrigir` com selecção marca highlights antigos negativos e selecção positiva; feedback não adquire slot `search`.

## Passos

- [ ] Testes de registo (acima).
- [ ] Commit: `test(feedback): falha sem registo Acertou/Corrigir/Descartar`.
- [ ] API + UI linha pequena; link para corrigir mais tarde.
- [ ] Boost runtime já coberto em PLN-09 — verificar integração.
- [ ] Job LoRA no escalonador estado `lora`; pausável por procura.
- [ ] Após treino: avaliar; se pior → rejeitar troca; se melhor → export ONNX atómico + actualizar `versoes_modelo`.
- [ ] Garantir `torch` só durante treino; teste de memória/mock `libertar_torch()`.
- [ ] Commit: `feat(feedback): pares e LoRA do juiz com gate`.
- [ ] Teste: durante LoRA, procura continua com ONNX antigo.
- [ ] Commit: `test(feedback): ONNX antigo durante treino`.
- [ ] Commit de fecho.

## Notas para o executor

- Isto não muda o E2B.
- Não somar ficheiros de pesos de várias pessoas — só o conjunto de correções (PLN-17).
