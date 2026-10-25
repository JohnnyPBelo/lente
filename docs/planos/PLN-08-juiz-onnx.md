# PLN-08: Juiz ONNX

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Carregar o cross-encoder mmarco MiniLM em ONNX int8 (~120 MB), residente; pontuar pares (pergunta, frase) para decidir highlights; sem prosa, sem Jev.
**Fronteira:** o que NÃO entra neste plano — LoRA/treino (PLN-16), fusão RRF (PLN-09), E2B, troca por outro modelo de decisão.
**Ficheiros futuros:**
- `engine/juiz/__init__.py`
- `engine/juiz/carregar.py` — ONNX Runtime, int8
- `engine/juiz/pontuar.py` — batch de pares → scores
- `engine/juiz/caminhos.py` — pesos locais se HF bloquear
- `tests/juiz/test_onnx_carga.py`
- `tests/juiz/test_pontuar.py`
**Teste que falha primeiro:** `tests/juiz/test_pontuar.py` — para pergunta e frase semanticamente alinhadas (sintéticas em PT), o score é **maior** que para um par claramente não relacionado; shapes e dtype estáveis; modelo em ONNX (não PyTorch residente).

## Passos

- [ ] Escrever teste de ordenação de scores com pares sintéticos.
- [ ] Commit: `test(juiz): falha sem pontuação ONNX`.
- [ ] Implementar carga ONNX Runtime; sessões thread-safe documentadas.
- [ ] Tokenização alinhada ao modelo Hugging Face original.
- [ ] `pontuar(pergunta, lista_frases) -> lista[float]`.
- [ ] Fazer passar (integração com pesos; unitários com mock da sessão).
- [ ] Commit: `feat(juiz): cross-encoder ONNX int8`.
- [ ] Teste: PyTorch **não** importado no caminho quente de pontuação.
- [ ] Teste: falha de download → erro tipado com caminho manual (app ainda pode abrir — PLN-21).
- [ ] Registar versão do juiz em `versoes_modelo`.
- [ ] Commit: `test(juiz): sem PyTorch no caminho quente`.
- [ ] Commit de fecho.

## Notas para o executor

- Modelo: `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` ONNX int8 publicado.
- Quem pinta highlight é o código; o juiz só decide o que passa o limiar (limiar em PLN-09).
