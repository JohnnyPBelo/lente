# Ordem de trabalho PLN-06

Fonte: `docs/planos/PLN-06-blocos-frases-e-embeddings.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Cortar texto indexado em blocos (~500 tokens EmbeddingGemma, overlap 50), segmentar frases com offsets/caixas, gerar embeddings 256d normalizados (float32) e persistir; modelo residente e congelado.

## Fronteira

o que NÃO entra neste plano — FTS5/pesquisa (PLN-07), juiz, E2B, visão/áudio do EmbeddingGemma, fine-tune do embedding.

## Teste que falha primeiro, no plano

`tests/embeddings/test_cortar.py` — dado texto cujo tokenizador produz >600 tokens, `cortar_blocos` devolve ≥2 blocos; overlap ≈50 tokens entre fim do bloco i e início do i+1; cada bloco ≤~500 tokens (± margem documentada).

Nesta ordem esse teste é `test_reg_ing_010`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-02
- PLN-03
- PLN-04
- PLN-05

## Ficheiros que este PR pode criar

- `engine/embeddings/__init__.py`
- `engine/embeddings/carregar.py` — load EmbeddingGemma 2 texto-only; caminho local se HF falhar
- `engine/embeddings/prefixos.py` — `title: … | text: …` para documentos
- `engine/embeddings/cortar.py` — blocos 500 / overlap 50
- `engine/embeddings/frases.py` — segmentação + offsets
- `engine/embeddings/indexar.py` — orquestra documento → blocos/frases/vectores
- `engine/embeddings/dispositivo.py` — CPU float32; GPU acelera o mesmo código
- `tests/embeddings/test_cortar.py`
- `tests/embeddings/test_embedding_dim.py`
- `tests/fixtures/embeddings/paragrafo_longo.txt`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- engine/pesquisa/ (PLN-07 e PLN-09), engine/juiz/, engine/resposta/
- encoders de visão e de áudio, FTS5, a UI

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

Unidade de embedding: bloco. Unidade de highlight: frase. Testes de carga usam double. O teste do caminho em falta não descarrega pesos. Float16 em CPU está proibido. Miniatura pequena gerada na indexação.

## Requisitos que este PR fecha

- `REQ-ING-010` fecha com `REG-ING-010`.
- `REQ-ING-011` fecha com `REG-ING-011`.
- `REQ-BUS-001` fecha com `REG-BUS-001`.
- `REQ-BUS-002` fecha com `REG-BUS-002`.
- `REQ-MOD-005` fecha com `REG-MOD-005`.
- `REQ-FOR-004` fecha com `REG-FOR-004`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/embeddings/test_cortar.py::test_reg_ing_010`
  - Dado texto cujo tokenizador produz mais de 600 tokens, quando se cortam blocos, então saem pelo menos dois, cada um até cerca de 500 tokens com a margem documentada, e a sobreposição entre blocos consecutivos é cerca de 50 tokens. Cada frase guardada tem offsets e, quando o formato as traz, caixas.
- `tests/embeddings/test_miniatura.py::test_reg_ing_011`
  - Dado um documento com página visualizável, quando a indexação acaba, então fica uma miniatura persistida e voltar a pedi-la não renderiza o PDF outra vez. Dado o carregador sem pesos, quando o Hugging Face não entrega o ficheiro, então a mensagem indica o caminho local e o teste não descarrega nada.
- `tests/embeddings/test_embedding_dim.py::test_reg_bus_001`
  - Dado uma frase sintética em CPU, quando se embute, então o vector tem 256 dimensões, norma L2 próxima de 1, dtype float32 e nenhum NaN. O caminho float16 não é usado. O carregamento é só texto, com vision_config e audio_config nulos.
- `tests/embeddings/test_prefixos.py::test_reg_bus_002`
  - Dado um bloco na indexação, quando se forma a entrada, então começa por title: título | text: conteúdo. Dado a lente investigar ou acreditação, então a query usa task: question answering | query: . Dado verificar ou assessment, então task: fact checking | query: . Dado procura curta, então task: search result | query: .
- `tests/embeddings/test_dispositivo.py::test_reg_mod_005`
  - Dado o mesmo código de embedding, quando há GPU e quando só há CPU, então não existe um segundo modo de produto: a CPU corre o fluxo e a GPU só o acelera.
- `tests/embeddings/test_sem_visao_audio.py::test_reg_for_004`
  - Dado o carregamento do EmbeddingGemma, quando os modelos sobem, então não se instancia encoder de visão nem stack de áudio. O OCR de scans continua a ser o Tesseract, não um encoder.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] Este PR não introduz copy de interface.

## Paralelo

Depois da onda 1. Pode avançar ao lado de PLN-08 e de PLN-10. PLN-07 espera pelos vectores deste plano.
