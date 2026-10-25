# Ordem de trabalho PLN-11

Fonte: `docs/planos/PLN-11-escritor-e2b-e-duas-portas.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Carregar Gemma 4 E2B QAT Q4 só na visita de escrita; gerar prosa a partir dos trechos aprovados pelo juiz; filtrar por duas portas (citação `[n]` válida + fidelidade do juiz); sem histórico de respostas no prompt; miniaturas/excertos podem existir sem E2B.

## Fronteira

o que NÃO entra neste plano — fine-tune E2B, exemplos de respostas no prompt, HTTP/UI completos, LoRA do juiz.

## Teste que falha primeiro, no plano

`tests/resposta/test_portas.py` — frase sem `[n]` é descartada; frase com `[99]` inexistente no pacote é descartada; frase com `[1]` cujo texto contradiz o trecho 1 (score juiz baixo) é descartada; frase fiel com `[1]` sobrevive.

Nesta ordem esse teste é `test_reg_res_004`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-08
- PLN-09

## Ficheiros que este PR pode criar

- `engine/resposta/__init__.py`
- `engine/resposta/e2b.py` — carga/descarga GGUF, limite de núcleos
- `engine/resposta/prompt.py` — montar contexto só com trechos desta procura (+ página aberta se aplicável)
- `engine/resposta/porta1_citacao.py` — exige `[n]` de trecho do pacote
- `engine/resposta/porta2_fiel.py` — juiz frase↔trecho citado
- `engine/resposta/filtrar.py` — pipeline das portas; se zero frases → excertos ou vazio
- `tests/resposta/test_portas.py`
- `tests/resposta/test_prompt.py`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- engine/feedback/, apps/ui/, engine/api/
- fine-tune do E2B e exemplos de respostas no prompt

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

O contrato de prosa é docs/modelos/duas-portas.md e docs/modelos/e2b.md. Não descarregar o BF16 de treino. Alertas e lacunas não chamam o escritor. Sem o GGUF, o módulo devolve excertos. Testes unitários usam double.

## Requisitos que este PR fecha

- `REQ-BUS-008` fecha com `REG-BUS-008`.
- `REQ-RES-001` fecha com `REG-RES-001`.
- `REQ-RES-002` fecha com `REG-RES-002`.
- `REQ-RES-003` fecha com `REG-RES-003`.
- `REQ-RES-004` fecha com `REG-RES-004`.
- `REQ-RES-005` fecha com `REG-RES-005`.
- `REQ-RES-006` fecha com `REG-RES-006`.
- `REQ-RES-007` fecha com `REG-RES-007`.
- `REQ-RES-008` fecha com `REG-RES-008`.
- `REQ-RES-010` fecha com `REG-RES-010`.
- `REQ-RES-011` fecha com `REG-RES-011`.
- `REQ-MOD-006` fecha com `REG-MOD-006`.
- `REQ-FOR-006` fecha com `REG-FOR-006`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/resposta/test_seguimento.py::test_reg_bus_008`
  - Dado uma pergunta anterior e um seguimento curto no mesmo chat, quando se envia, então a pesquisa recebe a query reescrita completa. As citações da resposta são trechos desta volta, não prosa antiga.
- `tests/resposta/test_prompt.py::test_reg_res_001`
  - Dado N trechos aprovados pelo juiz, quando se monta o contexto do E2B, então o pacote traz ficheiro, página e texto desses trechos e não a biblioteca inteira.
- `tests/resposta/test_prompt.py::test_reg_res_002`
  - Dado um chat com prosa anterior do assistente, quando se monta o prompt, então essa prosa não entra.
- `tests/resposta/test_prompt.py::test_reg_res_003`
  - Dado o leitor aberto numa página e uma pergunta sobre essa página, quando se monta o contexto, então o texto da página entra além dos trechos aprovados.
- `tests/resposta/test_portas.py::test_reg_res_004`
  - Dado uma frase sem [n] e outra com [99] fora do pacote, quando passa a primeira porta, então ambas saem. Dado uma frase com [1] de um trecho do pacote, então segue para a segunda porta.
- `tests/resposta/test_portas.py::test_reg_res_005`
  - Dado uma frase com [1] que o juiz marca como infiel, quando passa a segunda porta, então sai. Dado uma frase fiel com [1], então sobrevive.
- `tests/resposta/test_portas.py::test_reg_res_006`
  - Dado miniaturas já disponíveis e as portas ainda por concluir, quando se inspecciona o resultado, então não há prosa provisória. No fim só ficam frases que passaram as duas portas.
- `tests/resposta/test_portas.py::test_reg_res_007`
  - Dado todas as frases rejeitadas mas ainda com trechos, quando a mensagem fecha, então ficam excertos ou miniaturas e nenhuma prosa. Dado nada acima do limiar, então fica o aviso de vazio e nenhuma miniatura a fingir resultado.
- `tests/resposta/test_sem_e2b.py::test_reg_res_008`
  - Dado o E2B em falta e o juiz disponível, quando há resultados, então a resposta são excertos e miniaturas com documento e offsets, sem prosa e sem o processo cair.
- `tests/resposta/test_visita.py::test_reg_res_010`
  - Dado uma geração concluída, quando se liberta o escritor, então o E2B deixa de estar residente. Feedback não altera os pesos do E2B.
- `tests/resposta/test_sem_e2b_modos.py::test_reg_res_011`
  - Dado o modo alerta ou lacunas, quando se envia, então o escritor não é chamado. Dado procurar com prosa e uma lente activa, então a instrução de prosa dessa lente pode entrar no prompt, distinta dos prefixos de embedding.
- `tests/resposta/test_sem_bf16.py::test_reg_mod_006`
  - Dado o carregador do E2B, quando se listam os artefactos aceite, então só entra o GGUF Q4 de visita e o pacote de treino BF16 de cerca de 11 GB é recusado. O teste não descarrega pesos.
- `tests/resposta/test_prompt.py::test_reg_for_006`
  - Dado histórico de respostas e feedback positivo, quando se monta o prompt do E2B, então esse material não entra como exemplos.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] Este PR não introduz copy de interface.

## Paralelo

Pode avançar ao lado de PLN-13, PLN-16, PLN-19 e PLN-20. PLN-12 espera por este, por PLN-09 e por PLN-10.
