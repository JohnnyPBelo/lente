# Ordem de trabalho PLN-21

Fonte: `docs/planos/PLN-21-estados-vazios-a11y-e-comando-unico.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Cobrir estados vazios observáveis (biblioteca sem ficheiros, modelo a descarregar, prosa toda filtrada, página sem texto, URL recusada, conversa nova, procura sem documentos); acessibilidade (foco, teclado, rótulos, `prefers-reduced-motion` já exigido); um comando sobe UI+motor em `127.0.0.1:4317`; piso Python 3.11+ / Node 22 / 16 GB documentado; se HF bloquear download, a app abre e diz onde pôr o ficheiro.

## Fronteira

o que NÃO entra neste plano — novas funcionalidades de produto; Electron; segundo modo GPU.

## Teste que falha primeiro, no plano

`tests/runtime/test_comando_unico.py` — invocar o entrypoint em processo (ou módulo `engine.cli:main`) com porto de teste; após ready, `GET http://127.0.0.1:<porto>/` devolve 200 (UI ou placeholder); existe **um** listener na interface de loopback; com pesos E2B ausentes, o processo **não** termina — endpoint de saúde reporta `e2b: ausente` e procura ainda devolve excertos.

Nesta ordem esse teste é `test_reg_mod_001`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

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

## Ficheiros que este PR pode criar

- `apps/ui/src/components/vazios/BibliotecaVazia.tsx`
- `apps/ui/src/components/vazios/ModeloADescarregar.tsx`
- `apps/ui/src/components/vazios/ProsaFiltrada.tsx`
- `apps/ui/src/components/vazios/PaginaSemTexto.tsx`
- `apps/ui/src/components/vazios/UrlRecusada.tsx`
- `apps/ui/src/components/vazios/ConversaNova.tsx`
- `apps/ui/src/components/vazios/ProcuraSemDocumentos.tsx`
- `apps/ui/src/a11y/focos.ts` / checklist em testes
- `engine/runtime/pesos.py` — resolver caminhos; mensagens se em falta
- `scripts/lente` ou `pyproject.toml` entrypoint `lente`
- `README.md` (raiz) — secção «Como correr» actualizada quando o código existir
- `tests/runtime/test_comando_unico.py`
- `tests/ui/a11y/estados-vazios.test.tsx`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- funcionalidade nova de produto, Electron, um modo GPU separado
- reimplementar portas, SSRF, LoRA ou dossier: ligar os estados vazios aos códigos que já existem

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

Ligar os sete estados vazios às strings de docs/interface/copy.md e aos códigos de erro já existentes. O comando chama-se lente: aplica migrações, regista o que falta em models/ e escuta em 127.0.0.1:4317. HTTP-models-status, HTTP-models-guidance e HTTP-models-download não descarregam pesos nos testes; o download real fica atrás de um double. Pode acrescentar a secção Como correr no README.md. Não criar contas, áudio, nem um modo GPU.

## Requisitos que este PR fecha

- `REQ-MOD-001` fecha com `REG-MOD-001`.
- `REQ-MOD-002` fecha com `REG-MOD-002`.
- `REQ-MOD-007` fecha com `REG-MOD-007`.
- `REQ-MOD-008` fecha com `REG-MOD-008`.
- `REQ-MOD-009` fecha com `REG-MOD-009`.
- `REQ-VAZ-001` fecha com `REG-VAZ-001`.
- `REQ-A11-001` fecha com `REG-A11-001`.
- `REQ-SEG-003` fecha com `REG-SEG-003`.
- `REQ-FOR-008` fecha com `REG-FOR-008`.
- `REQ-FOR-009` fecha com `REG-FOR-009`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/runtime/test_comando_unico.py::test_reg_mod_001`
  - Dado o comando num porto livre de loopback, quando fica pronto, então GET / devolve 200, há um único listener em 127.0.0.1, as migrações foram aplicadas e o Node não fica nesse processo. Sem argumentos o porto é 4317. A rejeição de 0.0.0.0 é REG-SEG-002.
- `tests/runtime/test_piso.py::test_reg_mod_002`
  - Dado o arranque documentado, quando se lê o piso, então constam Python 3.11 ou superior, Node 22 e 16 GB de RAM. Dado uma versão de Python abaixo desse piso, quando o comando inicia, então falha ou avisa em vez de seguir calado.
- `tests/runtime/test_comando_unico.py::test_reg_mod_007`
  - Dado um download de modelo bloqueado, quando a aplicação arranca, então abre e a orientação indica o caminho em models/ onde colocar o ficheiro em falta, para o embedding, o juiz e o E2B. O teste não descarrega pesos.
- `tests/runtime/test_comando_unico.py::test_reg_mod_008`
  - Dado o E2B ausente, quando o processo sobe, então não termina e GET /health reporta modelos.escritor ausente, como no contrato. Os excertos da procura são REG-RES-008.
- `tests/runtime/test_residentes.py::test_reg_mod_009`
  - Dado uma procura fora da janela em que o E2B escreve, quando se listam os residentes, então estão o EmbeddingGemma e o juiz ONNX int8, e o E2B não fica residente. O dtype float32 é REG-BUS-001.
- `apps/ui/src/components/vazios/reg-vaz-001.test.tsx`
  - Dado cada um dos sete estados, biblioteca sem ficheiros, modelo a descarregar, prosa toda filtrada, página sem texto, URL recusada, conversa nova e procura sem documentos, quando a interface o mostra, então o título e o corpo são os de docs/interface/copy.md. Prosa filtrada não mostra prosa fantasma. Procura sem documentos não mostra miniaturas a fingir resultados.
- `apps/ui/src/a11y/reg-a11-001.test.tsx`
  - Dado prefers-reduced-motion reduce, quando se percorre mensagem, leque, leitor e recolher na aplicação integrada, então as animações encurtam e o leque e o leitor continuam utilizáveis.
- `apps/ui/src/a11y/reg-seg-003.test.tsx`
  - Dado a aplicação aberta, quando se procura login, permissões partilhadas ou sincronização, então esses controlos não existem.
- `tests/runtime/test_sem_contas.py::test_reg_for_008`
  - Dado a superfície HTTP montada, quando se listam rotas, então não há login, papéis de permissão nem sincronização entre dispositivos.
- `tests/runtime/test_sem_contas.py::test_reg_for_009`
  - Dado a interface e o runtime, quando se inventariam modalidades, então não há ditado, voz nem tipo de ficheiro de áudio, e não se carregam pesos de áudio.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] O texto visível vem de `docs/interface/copy.md`, sem frase inventada para o mesmo estado.

## Paralelo

Não. É a onda 6 e espera por PLN-01 a PLN-20 fundidos.
