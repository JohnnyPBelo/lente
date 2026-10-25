# Ordem de trabalho PLN-17

Fonte: `docs/planos/PLN-17-importar-e-exportar-correcoes.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Exportar JSON de correções (versão formato, id modelo base, pares pergunta/trecho/etiqueta/lente/hash); importar com pré-visualização (contagem, lentes, amostra de perguntas), confirmação obrigatória, dedupe por hash, recusa se modelo base diferente; treino junta locais+importadas a partir do base.

## Fronteira

o que NÃO entra neste plano — exportar binário LoRA; aplicar import sem confirmação; UI dentro do menu `+` (fica no estado da aprendizagem no topo da lateral).

## Teste que falha primeiro, no plano

`tests/feedback/test_export_import.py` — export produz JSON com `formato_versao` e `modelo_base_id`; import do mesmo ficheiro com `confirmar=False` **não** grava pares; com `confirmar=True` grava; segundo import não duplica hashes; ficheiro com `modelo_base_id` outro → `ModeloBaseIncompativel`.

Nesta ordem esse teste é `test_reg_fbk_014`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-16

## Ficheiros que este PR pode criar

- `engine/feedback/exportar_correcoes.py`
- `engine/feedback/importar_correcoes.py`
- `engine/feedback/schema_correcoes.py` — validação (alinhar a `docs/dados/correcoes.schema.json`)
- `apps/ui/src/components/aprendizagem/ExportarCorrecoes.tsx`
- `apps/ui/src/components/aprendizagem/ImportarCorrecoes.tsx`
- `tests/feedback/test_export_import.py`
- `tests/fixtures/feedback/correcoes.exemplo.json` — sintético

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- o menu + da barra (PLN-14): não acrescentar lá as acções
- engine/feedback/lora.py e validar_troca.py (PLN-16): chamar o pipeline, não o reescrever
- docs/dados/correcoes.schema.json: cumprir, não substituir

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

O ficheiro tem de validar contra docs/dados/correcoes.schema.json: format_version, base_model_id, corrections. O exemplo do contrato HTTP usa chaves em português; não criar um terceiro formato. A resposta HTTP leva as chaves do esquema. Endpoints: HTTP-corrections-export, HTTP-corrections-import-preview, HTTP-corrections-import-confirm. Nada se aplica antes da confirmação. O ecrã usa export.warning.

## Requisitos que este PR fecha

- `REQ-BAR-012` fecha com `REG-BAR-012`.
- `REQ-FBK-011` fecha com `REG-FBK-011`.
- `REQ-FBK-012` fecha com `REG-FBK-012`.
- `REQ-FBK-013` fecha com `REG-FBK-013`.
- `REQ-FBK-014` fecha com `REG-FBK-014`.
- `REQ-FBK-015` fecha com `REG-FBK-015`.
- `REQ-FBK-016` fecha com `REG-FBK-016`.
- `REQ-FBK-017` fecha com `REG-FBK-017`.
- `REQ-FBK-018` fecha com `REG-FBK-018`.
- `REQ-SEG-004` fecha com `REG-SEG-004`.
- `REQ-FOR-003` fecha com `REG-FOR-003`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `apps/ui/src/components/aprendizagem/reg-bar-012.test.tsx`
  - Dado o menu + ou /, quando se listam as entradas, então não há Exportar correções nem Importar correções.
- `tests/feedback/test_export_import.py::test_reg_fbk_011`
  - Dado dois pares com o mesmo hash, quando entram no conjunto, então contam uma vez.
- `tests/feedback/test_export_import.py::test_reg_fbk_012`
  - Dado correcções existentes, quando se exporta, então o JSON é aceite por docs/dados/correcoes.schema.json, com format_version, base_model_id e corrections de pergunta, trecho, etiqueta, lente e hash_par, e não traz pesos.
- `apps/ui/src/components/aprendizagem/reg-fbk-013.test.tsx`
  - Dado o ecrã de exportação, quando se mostra, então o aviso visível é a string export.warning de copy.md: os trechos saem da máquina.
- `tests/feedback/test_export_import.py::test_reg_fbk_014`
  - Dado um JSON válido, quando se pré-visualiza sem confirmar, então vê-se a contagem, as lentes e uma amostra de perguntas e nada é gravado. Dado a confirmação, então os pares entram e o treino fica agendado para quando a máquina estiver livre.
- `tests/feedback/test_export_import.py::test_reg_fbk_015`
  - Dado um JSON cujo base_model_id não é o do juiz instalado, quando se importa, então a importação é recusada e os exemplos não se misturam.
- `tests/feedback/test_export_import.py::test_reg_fbk_016`
  - Dado um ficheiro ainda não confirmado, incluindo um que invertia etiquetas ou um JSON inválido, quando se procura ou se valida, então o juiz fica como estava e não há escrita.
- `apps/ui/src/components/aprendizagem/reg-fbk-017.test.tsx`
  - Dado a barra lateral, quando se olha o estado da aprendizagem no topo, então estão as acções Exportar correções e Importar correções, e não estão no menu + nem no /.
- `tests/feedback/test_export_import.py::test_reg_fbk_018`
  - Dado correcções locais e importadas já confirmadas, quando o treino corre, então parte do modelo base e usa a união sem hashes repetidos. Dado uma procura a chegar, então o treino pede pausa ao escalonador. A retoma em si é REG-BUS-012.
- `tests/feedback/test_export_import.py::test_reg_seg_004`
  - Dado importar com confirmação falsa ou omissa, quando a função regressa, então não há linhas novas no conjunto do juiz.
- `tests/feedback/test_export_import.py::test_reg_for_003`
  - Dado um adaptador LoRA binário oferecido como forma de juntar afinações, quando se importa ou exporta, então o único artefacto aceite é o JSON de correcções e não há média nem soma de pesos.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] O texto visível vem de `docs/interface/copy.md`, sem frase inventada para o mesmo estado.

## Paralelo

Pode avançar ao lado de PLN-18, PLN-19, PLN-20, PLN-14 e PLN-15. Os ecrãs de aprendizagem são só os deste PR.
