# Convenções de implementação

## Língua

Interface, mensagens de erro visíveis, commits e documentação: português de Portugal. Identificadores de código: o que os planos já nomeiam (`aplicar_migracoes`, `BarraEscrita`). Não traduzir nomes de biblioteca.

Copy visível copia [docs/interface/copy.md](../interface/copy.md). Não inventar outra frase para o mesmo estado.

## Testes primeiro

Para cada passo de um PLN: o teste que falha, o mínimo que o faz passar, o commit. O teste nomeado em «Teste que falha primeiro» abre o plano. Dados de teste são sintéticos, como `docs/dados/exemplos/`.

## Commits

Uma frase em português, a dizer porquê. O plano sugere prefixos `test`, `feat`, `docs`, `chore` quando o passo é só isso. Não misturar dois PLN no mesmo commit.

## Ramos

Um ramo por plano, a partir de `main` actualizado: `pln-01-esquema`, `pln-02-texto`, e por aí fora. O pull request liga os requisitos que o plano cobre (a matriz de rastreio tem os IDs) e diz que testes passaram.

## Superfície

- O servidor escuta em `127.0.0.1`, porto `4317` em utilização normal. Se estiver ocupado, `python3 -m engine.cli --porta N` (a UI usa a mesma origem). Testes usam um porto livre de loopback.
- URL de artigo: resolver o nome e recusar loopback, link-local, privado e metadados, também depois de redirect.
- Hash diferente em disco marca o documento desactualizado. A resposta não usa o índice velho em silêncio.
- Correcções importadas não treinam antes de confirmação. O ecrã de exportação diz que os trechos saem da máquina.
- Não gerar procedimentos de ataque, não acrescentar contas, sincronização, áudio, nem um segundo modelo de decisão.

## Git

Não commitar `data/`, `models/`, `.venv`, `node_modules`, `.env`, GGUF, ONNX, safetensors, nem adaptadores LoRA. O que se partilha entre máquinas é o JSON de correcções, e só por acção explícita de quem exporta.

## Quando a especificação não chega

Se um plano e um ADR discordarem, o ADR ganha e o plano corrige-se no mesmo pull request. Se os dois discordarem de `docs/origem/plano.md`, ganha o plano de origem: não se reescreve esse ficheiro; abre-se a diferença no PR para decisão.
