# Ordem de trabalho PLN-16

Fonte: `docs/planos/PLN-16-feedback-e-lora-do-juiz.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

UI e API de feedback (Acertou, Corrigir, Descartar) sem bloquear a procura seguinte; persistir pares; quando a máquina está livre, treinar LoRA rank 8 do juiz (≤2 núcleos), validar contra holdout, exportar ONNX novo e libertar PyTorch; procuras usam ONNX anterior até sucesso.

## Fronteira

o que NÃO entra neste plano — import/export de ficheiro de correcções (PLN-17), fine-tune E2B, média de pesos LoRA de sítios diferentes.

## Teste que falha primeiro, no plano

`tests/feedback/test_registar.py` — `Descartar` não cria pares de treino; `Acertou` marca trechos mostrados positivos; `Corrigir` com selecção marca highlights antigos negativos e selecção positiva; feedback não adquire slot `search`.

Nesta ordem esse teste é `test_reg_fbk_002`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-08
- PLN-10

## Ficheiros que este PR pode criar

- `apps/ui/src/components/chat/FeedbackLinha.tsx`
- `engine/feedback/__init__.py`
- `engine/feedback/registar.py` — Acertou/Corrigir/Descartar
- `engine/feedback/lora.py` — treino rank 8, LR baixo, pull to base
- `engine/feedback/validar_troca.py` — rejeitar se holdout piorar
- `engine/feedback/exportar_onnx.py`
- `tests/feedback/test_registar.py`
- `tests/feedback/test_lora_gate.py`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- engine/feedback/exportar_correcoes.py e importar_correcoes.py (PLN-17)
- engine/resposta/ e o E2B
- apps/ui excepto FeedbackLinha.tsx

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

Isto não muda o E2B. Durante o LoRA a procura usa o ONNX anterior. O slot vem de PLN-10. Não somar ficheiros de pesos. Testes de treino usam double de PyTorch e não descarregam o modelo real.

## Requisitos que este PR fecha

- `REQ-JUI-004` fecha com `REG-JUI-004`.
- `REQ-JUI-005` fecha com `REG-JUI-005`.
- `REQ-FBK-001` fecha com `REG-FBK-001`.
- `REQ-FBK-002` fecha com `REG-FBK-002`.
- `REQ-FBK-003` fecha com `REG-FBK-003`.
- `REQ-FBK-004` fecha com `REG-FBK-004`.
- `REQ-FBK-005` fecha com `REG-FBK-005`.
- `REQ-FBK-006` fecha com `REG-FBK-006`.
- `REQ-FBK-008` fecha com `REG-FBK-008`.
- `REQ-FBK-009` fecha com `REG-FBK-009`.
- `REQ-FBK-010` fecha com `REG-FBK-010`.
- `REQ-FOR-007` fecha com `REG-FOR-007`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/feedback/test_registar.py::test_reg_jui_004`
  - Dado feedback aplicado, quando uma procura semelhante volta a correr, então a ordenação ou o limiar dos highlights muda no juiz. Os pesos do EmbeddingGemma e do E2B ficam iguais.
- `tests/feedback/test_lora_gate.py::test_reg_jui_005`
  - Dado treino LoRA do juiz, quando se observa a memória, então o PyTorch só está presente durante esse treino e sai no fim. Até um export aceite, a procura usa o ONNX anterior.
- `apps/ui/src/components/chat/reg-fbk-001.test.tsx`
  - Dado uma mensagem com highlights, quando está no fio, então vê-se Acertou, Corrigir e Descartar. Dado outra procura, então começa sem esperar por essas acções.
- `tests/feedback/test_registar.py::test_reg_fbk_002`
  - Dado Descartar confirmado, quando se inspecciona o conjunto de treino, então não há pares positivos nem negativos dessa mensagem e os pesos do juiz e do E2B não mudam.
- `apps/ui/src/components/chat/reg-fbk-003.test.tsx`
  - Dado uma mensagem sem correcção imediata, quando se procura o gesto, então existe o link Corrigir mais tarde e esse link abre o fluxo Corrigir.
- `tests/feedback/test_registar.py::test_reg_fbk_004`
  - Dado Acertou numa mensagem com trechos, quando se regista, então esses trechos ficam com etiqueta positivo.
- `tests/feedback/test_registar.py::test_reg_fbk_005`
  - Dado Corrigir com uma selecção, quando se regista, então as marcas da resposta ficam negativas e a selecção fica positiva.
- `tests/feedback/test_lora_gate.py::test_reg_fbk_006`
  - Dado Acertou ou Corrigir, quando se inspeccionam os artefactos, então o E2B não recebe fine-tune e o efeito fica no juiz.
- `tests/feedback/test_lora_gate.py::test_reg_fbk_008`
  - Dado correcções por treinar e a máquina livre de procura, quando o treino arranca, então é um LoRA rank 8 do juiz, a rejogar o conjunto, com learning rate baixo e puxão para o modelo base.
- `tests/feedback/test_lora_gate.py::test_reg_fbk_009`
  - Dado o LoRA a correr, quando se lê o limite de CPU do treino, então é no máximo dois núcleos.
- `tests/feedback/test_lora_gate.py::test_reg_fbk_010`
  - Dado um hold-out que piora, quando o treino acaba, então o ONNX em uso não é substituído. Dado um treino aceite, então exporta um ONNX novo, liberta o PyTorch e só depois a procura muda de modelo. Durante o treino, ou depois de rejeição, a procura usa o ONNX anterior.
- `tests/feedback/test_lora_gate.py::test_reg_for_007`
  - Dado feedback e treinos concluídos, quando se lista os jobs, então não há fine-tune nem LoRA do E2B. Só o juiz é treinável.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] O texto visível vem de `docs/interface/copy.md`, sem frase inventada para o mesmo estado.

## Paralelo

Pode avançar ao lado de PLN-09, PLN-11, PLN-12, PLN-13, PLN-14, PLN-15, PLN-18, PLN-19 e PLN-20. O único componente de UI deste PR é FeedbackLinha.
