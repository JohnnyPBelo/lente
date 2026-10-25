# Ordem de trabalho PLN-19

Fonte: `docs/planos/PLN-19-alertas.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Criar até 10 alertas a partir do modo Alerta; grupo «Alertas» na barra lateral; cada alerta é um fio; ao indexar documento **novo**, o juiz avalia só frases desse documento; se passar limiar, mensagem no fio com miniatura; documentos antigos não são revistos sozinhos; interruptor no topo do fio desliga.

## Fronteira

o que NÃO entra neste plano — reavaliar biblioteca inteira em fundo; E2B nos alertas; correlacionar via alerta.

## Teste que falha primeiro, no plano

`tests/alertas/test_avaliar_novo.py` — com alerta activo cuja query casa com frase de um documento acabado de indexar (juiz mock alto), cria-se mensagem no fio do alerta com `documento_id` e miniatura; reindexar o **mesmo** doc antigo sem ser «novo» na política → não dispara; alerta desligado → não dispara.

Nesta ordem esse teste é `test_reg_ale_005`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-06
- PLN-08

## Ficheiros que este PR pode criar

- `engine/alertas/__init__.py`
- `engine/alertas/criar.py`
- `engine/alertas/avaliar_documento.py` — chamado no fim da indexação
- `engine/alertas/limite.py` — máx. 10
- `apps/ui/src/components/alertas/GrupoAlertas.tsx`
- `apps/ui/src/components/alertas/FioAlerta.tsx`
- `tests/alertas/test_limite.py`
- `tests/alertas/test_avaliar_novo.py`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- engine/resposta/ e qualquer chamada ao E2B
- apps/ui/src/components/barra/ (PLN-14)
- varrer a biblioteca antiga

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

No máximo dez. O erro HTTP é limite_alertas. Avaliação só no fim da indexação de um documento novo. Sem E2B. Lente do alerta usa o prefixo já definido. HTTP-alerts-list, HTTP-alerts-create e HTTP-alerts-toggle.

## Requisitos que este PR fecha

- `REQ-ALE-001` fecha com `REG-ALE-001`.
- `REQ-ALE-002` fecha com `REG-ALE-002`.
- `REQ-ALE-003` fecha com `REG-ALE-003`.
- `REQ-ALE-004` fecha com `REG-ALE-004`.
- `REQ-ALE-005` fecha com `REG-ALE-005`.
- `REQ-ALE-006` fecha com `REG-ALE-006`.
- `REQ-ALE-007` fecha com `REG-ALE-007`.
- `REQ-FOR-002` fecha com `REG-FOR-002`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/alertas/test_criar.py::test_reg_ale_001`
  - Dado um texto de vigilância e menos de dez alertas, quando se cria, então o alerta fica persistido. O placeholder exposto é «O que queres que eu vigie?».
- `tests/alertas/test_limite.py::test_reg_ale_002`
  - Dado já dez alertas, quando se tenta criar o décimo primeiro, então a criação falha com o erro limite_alertas do contrato e continuam a existir dez.
- `apps/ui/src/components/alertas/reg-ale-003.test.tsx`
  - Dado pelo menos um alerta, quando se olha a barra lateral, então o grupo Alertas está por baixo das conversas, com o rótulo de copy.md.
- `tests/alertas/test_criar.py::test_reg_ale_004`
  - Dado um alerta, quando se abre, então tem um fio próprio, distinto das conversas de procura.
- `tests/alertas/test_avaliar_novo.py::test_reg_ale_005`
  - Dado um alerta activo e um documento novo acabado de indexar cuja frase o juiz de teste deixa passar, quando a avaliação corre, então só esse documento é lido e nasce uma mensagem no fio com o documento e a miniatura. O mesmo documento, se não for novo, não dispara. Um alerta desligado não dispara. O escritor não é chamado.
- `tests/alertas/test_avaliar_novo.py::test_reg_ale_006`
  - Dado um alerta criado depois de documentos já indexados, quando fica activo sem documento novo, então a biblioteca antiga não é relida para alimentar o fio.
- `apps/ui/src/components/alertas/reg-ale-007.test.tsx`
  - Dado o fio de um alerta, quando se usa o interruptor no topo, então o alerta deixa de emitir até voltar a ser ligado.
- `tests/alertas/test_avaliar_novo.py::test_reg_for_002`
  - Dado a aplicação em idle, com biblioteca grande e sem documento novo a indexar, quando o tempo passa, então não corre um job que reavalie sozinho todos os documentos para alertas ou highlights.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] O texto visível vem de `docs/interface/copy.md`, sem frase inventada para o mesmo estado.

## Paralelo

Pode avançar ao lado de PLN-07, PLN-09, PLN-10, PLN-11, PLN-12, PLN-13, PLN-16, PLN-18 e PLN-20. Não edita a barra de modos: essa é PLN-14.
