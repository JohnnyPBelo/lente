# Ordem de trabalho PLN-10

Fonte: `docs/planos/PLN-10-escalonador.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Garantir um trabalho pesado de cada vez: procura pausa indexação e LoRA e retoma-os no fim; reservar ≥2 núcleos para sistema/UI; limitar E2B a `nproc-2` e LoRA a 2 núcleos.

## Fronteira

o que NÃO entra neste plano — HTTP completo (PLN-12), UI de estados do escalonador (telemetria mínima ok), treino LoRA real (ganchos + stub).

## Teste que falha primeiro, no plano

`tests/escalonador/test_slot.py` — com indexação «em curso» (tarefa async/thread controlada), ao adquirir slot `search` a indexação observa pausa; após libertar search, a indexação retoma e conclui; nunca dois `search` em paralelo.

Nesta ordem esse teste é `test_reg_bus_012`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-01

## Ficheiros que este PR pode criar

- `engine/escalonador/__init__.py`
- `engine/escalonador/slot.py` — mutex/async lock do slot pesado
- `engine/escalonador/estados.py` — `idle|search|index|lora|paused_for_search`
- `engine/escalonador/nucleos.py` — cálculo de limites CPU
- `engine/escalonador/fila_ingestao.py` — um documento de cada vez
- `tests/escalonador/test_slot.py`
- `tests/escalonador/test_nucleos.py`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- engine/api/ (PLN-12), o treino LoRA real (PLN-16), apps/ui/
- engine/ingestao/ e engine/pesquisa/rrf.py

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

Trabalhos pesados: procura, incluindo correlacionar e lacunas, indexação, E2B dentro da procura, e LoRA. Feedback imediato é leve. GPU não cria segundo modo. Tabelas de núcleos para 4, 8 e 16 como em docs/arquitetura/escalonador.md.

## Requisitos que este PR fecha

- `REQ-ING-009` fecha com `REG-ING-009`.
- `REQ-BUS-012` fecha com `REG-BUS-012`.
- `REQ-MOD-003` fecha com `REG-MOD-003`.
- `REQ-MOD-004` fecha com `REG-MOD-004`.
- `REQ-DES-003` fecha com `REG-DES-003`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/escalonador/test_fila.py::test_reg_ing_009`
  - Dado dois documentos na fila, quando a indexação decorre, então só um está activo. O seguinte só começa quando o actual termina.
- `tests/escalonador/test_slot.py::test_reg_bus_012`
  - Dado indexação em curso, quando se adquire o slot de procura, então a indexação pausa e, ao libertar o slot, retoma e conclui. O mesmo acontece ao LoRA. Nunca há duas procuras pesadas ao mesmo tempo.
- `tests/escalonador/test_nucleos.py::test_reg_mod_003`
  - Dado 4, 8 e 16 núcleos, quando se calculam os limites, então ficam sempre pelo menos dois livres e o E2B fica no máximo com nproc-2, ou seja 2, 6 e 14.
- `tests/escalonador/test_estados.py::test_reg_mod_004`
  - Dado o slot ocupado, quando chega outro trabalho pesado que não seja a procura a preemptir, então o erro é fila ocupada. Gravar feedback imediato não adquire o slot de procura. Os estados observáveis são idle, search, index, lora e paused_for_search.
- `tests/escalonador/test_orcamento.py::test_reg_des_003`
  - Dado procura e indexação ao mesmo tempo, quando se lê o estado, então não estão as duas activas. Dado um pedido de miniatura, então devolve-se o ficheiro gravado na indexação e um renderer de PDF espião não é chamado.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] Este PR não introduz copy de interface.

## Paralelo

Pode avançar ao lado da onda 1, de PLN-06, PLN-07, PLN-08, PLN-13 e do motor de PLN-20. É o dono de engine/escalonador/.
