# Ordem de trabalho PLN-07

Fonte: `docs/planos/PLN-07-fts5-e-cosseno-exacto.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Ligar FTS5 e sqlite-vec no mesmo ficheiro SQLite; pesquisa lexical + varrimento de cosseno exacto 256d (sem índice aproximado); devolver candidatos unidos sem ainda fundir RRF nem juiz.

## Fronteira

o que NÃO entra neste plano — RRF/Platt (PLN-09), juiz (PLN-08), Qdrant/Chroma/LanceDB/Postgres, extensão Vec1 oficial do SQLite se for ANN.

## Teste que falha primeiro, no plano

`tests/pesquisa/test_cosseno_exacto.py` — inserir 3 vectores conhecidos; consulta com o vector idêntico ao #2 devolve `#2` em primeiro com score cosseno ≈ 1.0; nenhum vizinho omitido numa base de N pequenos.

Nesta ordem esse teste é `test_reg_bus_005`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-01
- PLN-06

## Ficheiros que este PR pode criar

- `engine/pesquisa/__init__.py`
- `engine/pesquisa/fts.py` — popular e consultar FTS5
- `engine/pesquisa/vec.py` — carregar extensão sqlite-vec; insert/query cosseno
- `engine/pesquisa/candidatos.py` — união embedding ∪ FTS (sem RRF ainda)
- `engine/armazenamento/esquema/002_fts_vec.sql` (se não estiver no 001)
- `tests/pesquisa/test_fts5.py`
- `tests/pesquisa/test_cosseno_exacto.py`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- engine/pesquisa/rrf.py, limiar.py, platt.py, pipeline.py (PLN-09)
- engine/juiz/, engine/embeddings/cortar.py
- o resto de engine/armazenamento/ além de esquema/002_fts_vec.sql

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

Um ficheiro SQLite leva documentos, FTS, vectores e chats. Se o varrimento deixar de caber em milissegundos, mantém-se exacto. Identificador literal nos candidatos FTS é REG-BUS-003; furar o chão de cosseno é REG-BUS-007, no PLN-09.

## Requisitos que este PR fecha

- `REQ-BUS-003` fecha com `REG-BUS-003`.
- `REQ-BUS-005` fecha com `REG-BUS-005`.
- `REQ-BUS-006` fecha com `REG-BUS-006`.
- `REQ-DES-001` fecha com `REG-DES-001`.
- `REQ-FOR-001` fecha com `REG-FOR-001`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/pesquisa/test_fts5.py::test_reg_bus_003`
  - Dado um bloco indexado com o identificador sintético CVE-2099-0001, quando a consulta FTS é esse termo, então o bloco entra nos candidatos antes do juiz.
- `tests/pesquisa/test_cosseno_exacto.py::test_reg_bus_005`
  - Dado três vectores conhecidos de 256 dimensões, quando se consulta com o vector idêntico ao segundo, então esse fica em primeiro com cosseno próximo de 1 e nenhum dos restantes é omitido. A stack não activa Vec1 nem outro índice aproximado.
- `tests/pesquisa/test_mesmo_ficheiro.py::test_reg_bus_006`
  - Dado um SQLite de teste com documentos, FTS e vectores, quando se copia o ficheiro e se reabre, então a pesquisa responde sem reindexar e não há processo à parte de Qdrant, Chroma, LanceDB ou Postgres.
- `tests/pesquisa/test_escala_exacta.py::test_reg_des_001`
  - Dado pelo menos dois mil vectores sintéticos de 256 dimensões, quando se pede o vizinho exacto, então ele é devolvido e não há ramo que passe a índice aproximado. O teste não descarrega modelos.
- `tests/pesquisa/test_sem_ann.py::test_reg_for_001`
  - Dado o caminho de produção da pesquisa, quando se inventariam imports e o tipo de índice, então não há Qdrant, Chroma, LanceDB, Postgres vectorial nem ANN. A procura semântica usa cosseno exacto no mesmo SQLite.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] Este PR não introduz copy de interface.

## Paralelo

Pode avançar ao lado de PLN-08 e de PLN-10, depois de PLN-06. PLN-09 espera por este e pelo PLN-08.
