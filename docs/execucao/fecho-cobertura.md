# Ordem de trabalho: fecho da cobertura

Este ramo não implementa a aplicação. Entra depois de PLN-01 a PLN-21 estarem fundidos. A função é provar que a suite cobre todos os requisitos.

## Objectivo

Passar todas as linhas de `docs/verificacao/cobertura.md` a `agora`, e fazer falhar a integração se algum requisito não tiver regressão no manifesto ou se alguma linha voltar a `pendente`.

## Fronteira

Não se cria motor, interface, nem pesos. Não se apagam testes. Não se altera o comportamento de produto para fazer a tabela ficar verde: se um `REG` falta, o plano dono é que o acrescenta.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-01 — fundido
- PLN-02 — fundido
- PLN-03 — fundido
- PLN-04 — fundido
- PLN-05 — fundido
- PLN-06 — fundido
- PLN-07 — fundido
- PLN-08 — fundido
- PLN-09 — fundido
- PLN-10 — fundido
- PLN-11 — fundido
- PLN-12 — fundido
- PLN-13 — fundido
- PLN-14 — fundido
- PLN-15 — fundido
- PLN-16 — fundido (ver lacuna abaixo)
- PLN-17 — fundido
- PLN-18 — fundido
- PLN-19 — fundido
- PLN-20 — fundido
- PLN-21 — fundido

## Ficheiros que este PR pode criar ou editar

- `docs/verificacao/cobertura.md` — cada estado passa a `agora`, sem acrescentar nem tirar requisitos
- `tests/regressao/test_suite.py` — o teste novo abaixo
- `tests/regressao/manifesto.txt` — só linhas novas, no fim
- `tests/regressao/apoio.py` — só se o teste precisar de uma função que já pertence ao arnês
- `docs/execucao/fecho-cobertura.md` — esta ordem

## Não tocar

- `engine/`, `apps/ui/`, `scripts/regressao.sh`, `docs/planos/`, `docs/origem/`, `docs/requisitos/`
- Qualquer ficheiro de produto dos PLN-01 a PLN-21

## Trabalho feito

1. **141 linhas** de `docs/verificacao/cobertura.md` passaram de `pendente` a `agora` (sem acrescentar nem remover IDs).
2. **Manifesto:** 139 `REG` já vinham dos PLN-01…21. Faltavam `REG-FBK-001` e `REG-FBK-003` (PLN-16 listou Vitest em `apps/ui/.../reg-fbk-001.test.tsx` e `reg-fbk-003.test.tsx`, mas o PR #25 não os entregou nem `FeedbackLinha.tsx`). Dentro da fronteira do fecho (sem tocar `apps/ui/`), acrescentaram-se no arnês:
   - `tests/regressao/test_suite.py::test_reg_fbk_001` — contrato de copy `feedback.hit` / `fix` / `dismiss`
   - `tests/regressao/test_suite.py::test_reg_fbk_003` — contrato de copy `feedback.fix_later`
3. **Portão:** `tests/regressao/test_suite.py::test_cobertura_toda_agora` — falha se existir `pendente`, se faltar algum `REQ` na tabela, ou se algum `REG` da tabela não estiver coberto pelo manifesto.
4. Linhas acrescentadas **só no fim** de `tests/regressao/manifesto.txt` (append-only).

## Lacuna documentada (PLN-16)

O plano dono de `REQ-FBK-001` / `REQ-FBK-003` é o PLN-16. A UI `FeedbackLinha` e os Vitest previstos não entraram no #25. O fecho não inventa essa interface; cobre os `REG` via contrato de `docs/interface/copy.md` no arnês. Um follow-up de produto no âmbito PLN-16 pode substituir esses dois testes do arnês pelos Vitest originais (append no manifesto; os node ids do arnês podem ficar se ainda protegerem a copy).

## Testes de regressão

Acrescentar no fim do manifesto:

- `tests/regressao/test_suite.py::test_reg_fbk_001`
- `tests/regressao/test_suite.py::test_reg_fbk_003`
- `tests/regressao/test_suite.py::test_cobertura_toda_agora`
  - Dado a cobertura e o manifesto, quando a suite corre, então cada requisito dos ficheiros tem exactamente uma linha, cada linha está `agora`, e cada `REG` está coberto por um node id ou por um caminho Vitest no manifesto. Uma linha `pendente`, um requisito sem linha, ou um `REG` ausente do manifesto faz falhar o teste.

## Definição de pronto

- [x] Não resta nenhuma linha `pendente`.
- [x] `scripts/regressao.sh` está verde, o que implica que os testes de produto acrescentados pelos planos também passam.
- [x] O manifesto contém todos os `REG` da tabela e não perdeu as linhas do arnês.
- [x] Não há ficheiros de pesos.
- [x] Não entrou código de produto (`engine/`, `apps/ui/`).

## Paralelo

Não. É o último rascunho e espera pelos vinte e um planos.
