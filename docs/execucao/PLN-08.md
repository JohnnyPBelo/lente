# Ordem de trabalho PLN-08

Fonte: `docs/planos/PLN-08-juiz-onnx.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Carregar o cross-encoder mmarco MiniLM em ONNX int8 (~120 MB), residente; pontuar pares (pergunta, frase) para decidir highlights; sem prosa, sem Jev.

## Fronteira

o que NÃO entra neste plano — LoRA/treino (PLN-16), fusão RRF (PLN-09), E2B, troca por outro modelo de decisão.

## Teste que falha primeiro, no plano

`tests/juiz/test_pontuar.py` — para pergunta e frase semanticamente alinhadas (sintéticas em PT), o score é **maior** que para um par claramente não relacionado; shapes e dtype estáveis; modelo em ONNX (não PyTorch residente).

Nesta ordem esse teste é `test_reg_jui_002`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-01

## Ficheiros que este PR pode criar

- `engine/juiz/__init__.py`
- `engine/juiz/carregar.py` — ONNX Runtime, int8
- `engine/juiz/pontuar.py` — batch de pares → scores
- `engine/juiz/caminhos.py` — pesos locais se HF bloquear
- `tests/juiz/test_onnx_carga.py`
- `tests/juiz/test_pontuar.py`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- engine/feedback/ e o treino LoRA (PLN-16)
- engine/pesquisa/rrf.py (PLN-09), engine/resposta/, apps/ui/

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

Modelo cross-encoder/mmarco-mMiniLMv2-L12-H384-v1, ONNX int8. O limiar é PLN-09. Registar a versão em versoes_modelo. Falha de pesos devolve erro tipado com caminho manual, sem descarregar.

## Requisitos que este PR fecha

- `REQ-JUI-001` fecha com `REG-JUI-001`.
- `REQ-JUI-002` fecha com `REG-JUI-002`.
- `REQ-FOR-005` fecha com `REG-FOR-005`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/juiz/test_onnx_carga.py::test_reg_jui_001`
  - Dado a configuração do juiz, quando se identifica o modelo, então é o ONNX int8 de cross-encoder/mmarco-mMiniLMv2-L12-H384-v1, ficheiro avx512 ou arm64 conforme a máquina, e não pesos Jev nem um Qwen ou DeBERTa no lugar do juiz.
- `tests/juiz/test_pontuar.py::test_reg_jui_002`
  - Dado uma pergunta e uma frase sintéticas alinhadas em português, e um par claramente alheio, quando se pontua, então o score alinhado é maior. O resultado é pontuação, sem prosa, e o caminho quente não importa PyTorch. O teste usa double da sessão, sem descarregar pesos.
- `tests/juiz/test_sem_outro_decisor.py::test_reg_for_005`
  - Dado o carregador do juiz, quando se lista o decisor, então não há cliente Jev nem substituição por outro modelo. O único identificador aceite é o mmarco deste plano.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] Este PR não introduz copy de interface.

## Paralelo

Pode avançar assim que PLN-01 estiver fundido, ao lado de PLN-06, PLN-07 e PLN-10. Os testes usam pares sintéticos e um double da sessão ONNX. Não descarrega pesos.
