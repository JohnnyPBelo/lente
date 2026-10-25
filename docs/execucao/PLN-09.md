# Ordem de trabalho PLN-09

Fonte: `docs/planos/PLN-09-fusao-rrf-limiar-e-platt.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Fundir rankings FTS e embedding por Reciprocal Rank Fusion; aplicar limiar visível do juiz; com correções suficientes, calibrar scores com escala de Platt nos exemplos do utilizador; privilegio imediato a trechos confirmados/rejeitados sem injectar texto no escritor.

## Fronteira

o que NÃO entra neste plano — treino LoRA (PLN-16), escrita E2B, UI do limiar (pode expor valor na API).

## Teste que falha primeiro, no plano

`tests/pesquisa/test_rrf.py` — dados duas listas ordenadas com ids sobrepostos, `rrf(a, b, k=60)` coloca no topo um id que está bem ranqueado em ambas; ids só numa lista ficam abaixo desse consenso.

Nesta ordem esse teste é `test_reg_bus_004`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-07
- PLN-08

## Ficheiros que este PR pode criar

- `engine/pesquisa/rrf.py`
- `engine/pesquisa/limiar.py`
- `engine/pesquisa/platt.py`
- `engine/pesquisa/pipeline.py` — candidatos → RRF → juiz → filtro limiar
- `engine/pesquisa/feedback_runtime.py` — boost/penalização por feedback recente
- `tests/pesquisa/test_rrf.py`
- `tests/pesquisa/test_limiar_platt.py`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- engine/feedback/lora.py (PLN-16), engine/resposta/, apps/ui/
- a criação do FTS e do sqlite-vec, que é PLN-07

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

k de omissão do RRF é 60. Platt só com o mínimo documentado de correcções; abaixo disso a escala é a identidade. Não injectar texto de feedback no E2B. Prefixo de query pode ser stub até PLN-14, mas REG-BUS-002 já fixa as strings no PLN-06.

## Requisitos que este PR fecha

- `REQ-BUS-004` fecha com `REG-BUS-004`.
- `REQ-BUS-007` fecha com `REG-BUS-007`.
- `REQ-BUS-010` fecha com `REG-BUS-010`.
- `REQ-FBK-007` fecha com `REG-FBK-007`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/pesquisa/test_rrf.py::test_reg_bus_004`
  - Dado duas listas ordenadas com identificadores sobrepostos e k 60, quando se funde por RRF, então um id bem colocado nas duas fica à frente dos que só aparecem numa. Highlight só depois do juiz deixar passar.
- `tests/pesquisa/test_literal.py::test_reg_bus_007`
  - Dado um candidato com identificador literal e cosseno abaixo do chão semântico, quando se filtra antes do juiz, então o candidato mantém-se. Dado o juiz a rejeitá-lo, então não há highlight forçado.
- `tests/pesquisa/test_limiar_platt.py::test_reg_bus_010`
  - Dado correcções acima do mínimo documentado, quando a calibração corre, então a escala de Platt aplica-se às pontuações seguintes e é monótona na fixture. Dado correcções a menos, então a escala é a identidade. Dado nada acima do limiar, então a lista de highlights fica vazia.
- `tests/pesquisa/test_feedback_runtime.py::test_reg_fbk_007`
  - Dado correcções positivas e negativas recentes, quando uma pergunta muito parecida devolve candidatos, então os confirmados sobem e os rejeitados descem entre esses candidatos. O texto do feedback não entra no prompt do escritor.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] Este PR não introduz copy de interface.

## Paralelo

Pode avançar ao lado de PLN-10, PLN-13, PLN-19 e PLN-20 se os ficheiros não se cruzarem. PLN-11 espera por este.
