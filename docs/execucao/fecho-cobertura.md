# Ordem de trabalho: fecho da cobertura

Este ramo não implementa a aplicação. Entra depois de PLN-01 a PLN-21 estarem fundidos. A função é provar que a suite cobre todos os requisitos.

## Objectivo

Passar todas as linhas de `docs/verificacao/cobertura.md` a `agora`, e fazer falhar a integração se algum requisito não tiver regressão no manifesto ou se alguma linha voltar a `pendente`.

## Fronteira

Não se cria motor, interface, nem pesos. Não se apagam testes. Não se altera o comportamento de produto para fazer a tabela ficar verde: se um `REG` falta, o plano dono é que o acrescenta.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-01
- PLN-02
- PLN-03
- PLN-04
- PLN-05
- PLN-06
- PLN-07
- PLN-08
- PLN-09
- PLN-10
- PLN-11
- PLN-12
- PLN-13
- PLN-14
- PLN-15
- PLN-16
- PLN-17
- PLN-18
- PLN-19
- PLN-20
- PLN-21

## Ficheiros que este PR pode criar ou editar

- `docs/verificacao/cobertura.md` — cada estado passa a `agora`, sem acrescentar nem tirar requisitos
- `tests/regressao/test_suite.py` — o teste novo abaixo
- `tests/regressao/manifesto.txt` — só a linha nova, no fim
- `tests/regressao/apoio.py` — só se o teste precisar de uma função que já pertence ao arnês

## Não tocar

- `engine/`, `apps/ui/`, `scripts/regressao.sh`, `docs/planos/`, `docs/origem/`, `docs/requisitos/`
- Qualquer ficheiro de produto dos PLN-01 a PLN-21

## Testes de regressão

Acrescentar no fim do manifesto:

- `tests/regressao/test_suite.py::test_cobertura_toda_agora`
  - Dado a cobertura e o manifesto, quando a suite corre, então cada requisito dos ficheiros tem exactamente uma linha, cada linha está `agora`, e cada `REG` está coberto por um node id ou por um caminho Vitest no manifesto. Uma linha `pendente`, um requisito sem linha, ou um `REG` ausente do manifesto faz falhar o teste.

## Definição de pronto

- [ ] Não resta nenhuma linha `pendente`.
- [ ] `scripts/regressao.sh` está verde, o que implica que os testes de produto acrescentados pelos planos também passam.
- [ ] O manifesto contém todos os `REG` da tabela e não perdeu as linhas do arnês.
- [ ] Não há ficheiros de pesos.
- [ ] Não entrou código de produto.

## Paralelo

Não. É o último rascunho e espera pelos vinte e um planos.
