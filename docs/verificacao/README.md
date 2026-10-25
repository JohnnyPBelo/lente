# Verificação

Cem por cento, neste repositório, quer dizer três coisas ao mesmo tempo.

1. Cada identificador `REQ-*` dos ficheiros em `docs/requisitos/` tem uma regressão estável na [cobertura](cobertura.md).
2. Cada plano PLN-01 … PLN-21 tem um pull request em rascunho, com a ordem de trabalho, os requisitos que fecha e os testes que tem de acrescentar ao manifesto.
3. O GitHub Actions corre `scripts/regressao.sh` em cada pull request e em cada push para `main`. A suite tem de ficar verde antes de o código entrar em `main`.

A aplicação ainda não está implementada. A suite que já corre é a do arnês. As regressões de produto ficam `pendente` até o plano dono as acrescentar e o fecho as marcar `agora`.

## Como um agente escolhe trabalho

1. Abrir os rascunhos. Cada um parte de `main` e só acrescenta `docs/execucao/`, com a ordem. Não traz código de produto.
2. Escolher um rascunho cujas dependências já estão fundidas em `main`. A ordem das ondas está em [docs/desenvolvimento/ondas.md](../desenvolvimento/ondas.md). O corpo do rascunho nomeia os outros pull requests que têm de entrar primeiro.
3. Respeitar a secção **Não tocar**. Esses caminhos pertencem a planos irmãos. Trabalho em paralelo só é seguro dentro dos ficheiros que o rascunho autoriza a criar.
4. Implementar no ramo desse rascunho, com o teste que falha primeiro, e acrescentar no fim de `tests/regressao/manifesto.txt` exactamente os `REG` listados. Não se apagam linhas.
5. Não editar `docs/verificacao/cobertura.md` num plano de produto. Essa tabela e a prova de que o manifesto cobre todos os `REG` são do rascunho de fecho, depois dos vinte e um planos.

Regras da suite: [docs/desenvolvimento/regressao.md](../desenvolvimento/regressao.md).

## O que não é cem por cento

Um plano com as caixas marcadas e a suite verde, mas com um `REQ` ainda `pendente` e ausente do manifesto, não fecha o produto. O fecho é que torna isso visível: passa todas as linhas a `agora` e a integração falha se algum requisito não tiver regressão recolhida.
