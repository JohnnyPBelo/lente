# Ordem de trabalho PLN-18

Fonte: `docs/planos/PLN-18-dossier.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Fechar dossier sob pedido (botão, não automático): fotografia no SQLite com perguntas, frases, trechos literais, ficheiro, página, offsets, caixas, score do juiz, SHA-256, data e versões dos modelos; reabrir sem correr modelos; se hash do ficheiro mudou, avisar mantendo prova antiga; export Markdown + JSON.

## Fronteira

o que NÃO entra neste plano — reindexação automática ao detectar mudança; cloud sync.

## Teste que falha primeiro, no plano

`tests/dossier/test_fechar_reabrir.py` — fechar conversa fixture grava fotografia; apagar pesos/mocks de modelos e `reabrir` devolve as mesmas frases/offsets sem chamar embedding/juiz/E2B; alterar bytes do ficheiro fonte → flag `fonte_alterada=True` e prova antiga intacta.

Nesta ordem esse teste é `test_reg_dos_004`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-01
- PLN-12

## Ficheiros que este PR pode criar

- `engine/dossier/__init__.py`
- `engine/dossier/fechar.py`
- `engine/dossier/reabrir.py`
- `engine/dossier/exportar.py` — Markdown + JSON
- `engine/dossier/integridade.py` — comparar SHA actual vs fotografia
- `apps/ui/src/components/dossier/BotaoFecharDossier.tsx`
- `apps/ui/src/components/dossier/VistaDossier.tsx`
- `tests/dossier/test_fechar_reabrir.py`
- `tests/dossier/test_export.py`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- reindexação ao detectar hash diferente, e qualquer sync
- apps/ui/src/components/leitor/ (PLN-15): ligar o link, não reimplementar o leitor
- engine/resposta/

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

O JSON de arquivo valida contra docs/dados/dossier.schema.json. O GET do contrato expõe fonte_alterada. Mapear entre os dois sem inventar um terceiro molde. HTTP-dossier-close, HTTP-dossier-get e HTTP-dossier-export. Fechar é botão, nunca automático. Reabrir não corre modelos.

## Requisitos que este PR fecha

- `REQ-DOS-003` fecha com `REG-DOS-003`.
- `REQ-DOS-004` fecha com `REG-DOS-004`.
- `REQ-DOS-005` fecha com `REG-DOS-005`.
- `REQ-DOS-006` fecha com `REG-DOS-006`.
- `REQ-DOS-007` fecha com `REG-DOS-007`.
- `REQ-DOS-008` fecha com `REG-DOS-008`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/dossier/test_fechar_reabrir.py::test_reg_dos_003`
  - Dado uma conversa com prova, quando chegam mensagens sem o botão de fechar, então não se grava fotografia. Dado o botão Fechar dossier, quando se activa, então a fotografia passa a existir.
- `tests/dossier/test_fechar_reabrir.py::test_reg_dos_004`
  - Dado um dossier acabado de fechar, quando se lê o SQLite, então há perguntas, frases, trecho literal, ficheiro, página, offsets, caixas e pontuação do juiz. Dado reabrir, então não se chama EmbeddingGemma, juiz nem E2B.
- `tests/dossier/test_fechar_reabrir.py::test_reg_dos_005`
  - Dado um dossier que cita ficheiros, quando se lê a fotografia, então cada fonte tem o SHA-256 dos bytes no momento do fecho.
- `tests/dossier/test_fechar_reabrir.py::test_reg_dos_006`
  - Dado um dossier fechado, quando se lê a fotografia, então há data e as versões do EmbeddingGemma, do juiz, com LoRA se existir, e do E2B.
- `tests/dossier/test_fechar_reabrir.py::test_reg_dos_007`
  - Dado o ficheiro fonte inalterado, quando se reabre, então vê-se a prova da fotografia. Dado um SHA-256 diferente no disco, então fonte_alterada fica verdadeiro e os trechos e as pontuações antigos continuam legíveis. Não há reindexação automática.
- `tests/dossier/test_export.py::test_reg_dos_008`
  - Dado um dossier fechado, quando se exporta, então há Markdown legível e um JSON com os mesmos campos, aceite por docs/dados/dossier.schema.json.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] O texto visível vem de `docs/interface/copy.md`, sem frase inventada para o mesmo estado.

## Paralelo

Pode avançar ao lado de PLN-16, PLN-17, PLN-19, PLN-20, PLN-14 e PLN-15. Os componentes de dossier não são o leitor nem a barra.
