# Arranque do desenvolvimento

A especificação já está no ramo `main`. Este directório é o que se lê **antes** de criar `engine/` ou `apps/ui/`.

## Ordem

1. [ambiente.md](ambiente.md) — o que instalar, onde ficam os pesos, o que não se descarrega.
2. [mapa-codigo.md](mapa-codigo.md) — pacote Python ou pasta da UI de cada plano. Resolve a diferença entre os papéis em `docs/estrutura/arvore.md` e os caminhos em `docs/planos/`.
3. [ondas.md](ondas.md) — o que pode avançar em paralelo e o que espera pelo plano anterior.
4. [convencoes.md](convencoes.md) — testes, commits, língua, o que nunca entra no git.
5. [glossario.md](glossario.md) — termos do plano com o sítio onde estão fechados.

O primeiro código é o [PLN-01](../planos/PLN-01-esquema-sqlite-e-migracoes.md): esquema SQLite e migrações, sem modelos e sem HTTP.

## Feito quando

Um plano está feito quando todas as caixas desse ficheiro estão marcadas e os testes que ele nomeia passam. Um requisito está feito quando os critérios Dado / Quando / Então em `docs/requisitos/` passam. A matriz em [docs/rastreio/matriz.md](../rastreio/matriz.md) diz que secção do plano de origem cada um cobre.

## O que esta pasta não faz

Não substitui ADRs, requisitos nem o contrato HTTP. Se um guia daqui divergir de `docs/origem/plano.md` ou de um ADR, ganha o plano de origem e depois o ADR.
