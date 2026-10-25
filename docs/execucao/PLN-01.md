# Ordem de trabalho PLN-01

Fonte: `docs/planos/PLN-01-esquema-sqlite-e-migracoes.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Criar a camada de armazenamento local: ficheiro SQLite em `data/`, esquema inicial alinhado a `docs/dados/esquema.md` (quando existir no ramo principal) e motor de migrações versionadas, sem modelos nem HTTP.

## Fronteira

o que NÃO entra neste plano — ingestão de ficheiros, embeddings, FTS5/sqlite-vec além do schema mínimo necessário para as tabelas, API, UI, juiz, E2B.

## Teste que falha primeiro, no plano

`tests/armazenamento/test_migracoes.py` — após `aplicar_migracoes(caminho_tmp)`, `PRAGMA user_version` ≥ 1 e existem as tabelas `documentos`, `documento_hashes`, `blocos`, `frases` (consulta a `sqlite_master`).

Nesta ordem esse teste é `test_reg_mig_001`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- Nenhuma. Pode partir de `main`.

## Ficheiros que este PR pode criar

- `engine/armazenamento/__init__.py`
- `engine/armazenamento/caminho.py` — resolve `data/` e o nome do ficheiro `.sqlite`
- `engine/armazenamento/ligacao.py` — abre ligação, PRAGMA (FK, WAL)
- `engine/armazenamento/migracoes.py` — aplica migrações em ordem
- `engine/armazenamento/esquema/001_inicial.sql` — tabelas base (documentos, hashes, blocos, frases, conversas, mensagens, fila, versoes_modelo, …)
- `engine/armazenamento/repositorio.py` — helpers mínimos (abrir, estado do esquema)
- `tests/armazenamento/test_migracoes.py`
- `tests/armazenamento/conftest.py` — tmp `data/` por teste

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- engine/ingestao/, engine/embeddings/, engine/pesquisa/, engine/juiz/, engine/escalonador/, engine/resposta/, engine/api/
- engine/feedback/, engine/dossier/, engine/alertas/, engine/diario/, engine/biblioteca/, engine/backup/, engine/runtime/, apps/ui/
- engine/armazenamento/esquema/002_fts_vec.sql, que é do PLN-07

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

docs/dados/esquema.md já está em main: o SQL 001 segue esse ficheiro. A frase do plano sobre o esquema «quando existir» está ultrapassada. Datas em texto ISO-8601 UTC. Booleanos como inteiros 0 ou 1. Não ligar sqlite-vec nem FTS5 além da estrutura vazia que o SQL 001 exigir. O directório de teste é temporário, nunca data/ do programador.

## Requisitos que este PR fecha

Nenhum requisito de produto fecha neste plano. O esquema é a base dos seguintes. A porta de entrada é REG-MIG-001.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/armazenamento/test_migracoes.py::test_reg_mig_001`
  - Dado um SQLite temporário, quando se aplicam as migrações, então user_version é pelo menos 1 e existem as tabelas documentos, documento_hashes, blocos e frases. A segunda chamada não falha nem recria tabelas. Uma chave estrangeira impede um bloco com documento inexistente. O estado do documento só aceita ok, desactualizado, a_indexar ou erro.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] Este PR não introduz copy de interface.

## Paralelo

Não. É a onda 0. Nenhum outro plano grava estado antes deste estar fundido.
