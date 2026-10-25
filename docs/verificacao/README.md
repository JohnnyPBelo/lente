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

## Rascunhos

Há 22 pull requests em rascunho: PLN-01 a PLN-21 e o fecho. Cada um só acrescenta a ordem em `docs/execucao/`. O código de produto entra quando um agente pega no rascunho, com as dependências já fundidas.

### Onda 0 — sozinho

- [PLN-01](https://github.com/JohnnyPBelo/lente/pull/10) esquema SQLite. Nada grava estado antes disto.

### Onda 1 — depois do PLN-01

Em paralelo, assim que o PLN-01 estiver fundido:

- [PLN-02](https://github.com/JohnnyPBelo/lente/pull/11) texto, Markdown e docx.
- [PLN-10](https://github.com/JohnnyPBelo/lente/pull/19) escalonador.

Depois do PLN-02, em paralelo entre si:

- [PLN-03](https://github.com/JohnnyPBelo/lente/pull/12) PDF com texto.
- [PLN-05](https://github.com/JohnnyPBelo/lente/pull/14) URL e recusa de endereços privados.

[PLN-04](https://github.com/JohnnyPBelo/lente/pull/13) OCR espera pelo PLN-03 e pode então avançar ao lado do PLN-05 e do PLN-10.

### Onda 2 — encontrar e decidir

- [PLN-06](https://github.com/JohnnyPBelo/lente/pull/15) embeddings, depois de PLN-02 a PLN-05.
- [PLN-08](https://github.com/JohnnyPBelo/lente/pull/17) juiz. Pode avançar ao lado de PLN-06, PLN-07 e PLN-10 assim que o PLN-01 estiver fundido. Testes com pares sintéticos, sem descarregar pesos.
- [PLN-07](https://github.com/JohnnyPBelo/lente/pull/16) FTS5 e cosseno exacto, depois de PLN-01 e PLN-06. Pode avançar ao lado do PLN-08.

### Onda 3 — uma procura com prova

- [PLN-09](https://github.com/JohnnyPBelo/lente/pull/18) fusão, depois de PLN-07 e PLN-08.
- [PLN-11](https://github.com/JohnnyPBelo/lente/pull/20) escritor e duas portas, depois de PLN-08 e PLN-09.
- [PLN-12](https://github.com/JohnnyPBelo/lente/pull/21) API HTTP, depois de PLN-09, PLN-10 e PLN-11.

### Onda 4 — interface

- [PLN-13](https://github.com/JohnnyPBelo/lente/pull/22) chrome. Pode avançar já, com respostas falsas, ao lado do motor.
- [PLN-14](https://github.com/JohnnyPBelo/lente/pull/23) barra e [PLN-15](https://github.com/JohnnyPBelo/lente/pull/24) leque e leitor, depois do PLN-13. Entre si só em paralelo se cada um ficar nos directórios da sua ordem e não reescrever `App.tsx`.

### Onda 5 — o que distingue a Lente

Podem avançar em paralelo quando as dependências de cada um estiverem fundidas, sem partilhar ficheiros:

- [PLN-16](https://github.com/JohnnyPBelo/lente/pull/25) feedback e LoRA, depois de PLN-08 e PLN-10.
- [PLN-17](https://github.com/JohnnyPBelo/lente/pull/26) importar e exportar correcções, depois do PLN-16.
- [PLN-18](https://github.com/JohnnyPBelo/lente/pull/27) dossier, depois de PLN-01 e PLN-12.
- [PLN-19](https://github.com/JohnnyPBelo/lente/pull/28) alertas, depois de PLN-06 e PLN-08.
- [PLN-20](https://github.com/JohnnyPBelo/lente/pull/29) diário, etiquetas e cópia. O motor espera só pelo PLN-01; a lista na interface espera pelo PLN-13.

### Onda 6 — fecho do produto

- [PLN-21](https://github.com/JohnnyPBelo/lente/pull/30) estados vazios, acessibilidade e comando único, depois de PLN-01 a PLN-20.

### Fecho da suite

- [Fecho](https://github.com/JohnnyPBelo/lente/pull/31) passa a cobertura a `agora` e faz falhar a integração se algum requisito ficar sem regressão. Espera por PLN-01 a PLN-21. Só toca em `docs/verificacao/cobertura.md` e em `tests/regressao/`.

## O que não é cem por cento

Um plano com as caixas marcadas e a suite verde, mas com um `REQ` ainda `pendente` e ausente do manifesto, não fecha o produto. O fecho é que torna isso visível: passa todas as linhas a `agora` e a integração falha se algum requisito não tiver regressão recolhida.
