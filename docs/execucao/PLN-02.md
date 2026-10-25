# Ordem de trabalho PLN-02

Fonte: `docs/planos/PLN-02-texto-markdown-e-docx.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Extrair texto e metadados mínimos de entradas `.txt`, Markdown e `.docx`, calcular SHA-256, e registar o documento na biblioteca com estado `a_indexar` ou `ok` conforme o fluxo de fila (sem embeddings ainda).

## Fronteira

o que NÃO entra neste plano — PDF, OCR, URL, corte em blocos/embeddings, FTS, UI de importação (só API/função de motor se útil para testes).

## Teste que falha primeiro, no plano

`tests/ingestao/test_texto_md_docx.py` — `extrair("…/amostra.md")` devolve texto contendo um parágrafo conhecido e lista de títulos não vazia; `sha256_ficheiro` devolve hex de 64 chars estável.

Nesta ordem esse teste é `test_reg_ing_002`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-01

## Ficheiros que este PR pode criar

- `engine/ingestao/__init__.py`
- `engine/ingestao/hash.py` — SHA-256 dos bytes
- `engine/ingestao/tipos.py` — discriminar extensão / MIME
- `engine/ingestao/texto.py` — `.txt` (UTF-8 com fallbacks documentados)
- `engine/ingestao/markdown.py` — `.md` / `.markdown` → texto + títulos para sumário
- `engine/ingestao/docx.py` — `.docx` → texto plano por parágrafo
- `engine/ingestao/registo.py` — upsert em `documentos` + `documento_hashes` + enfileirar
- `tests/ingestao/test_hash.py`
- `tests/ingestao/test_texto_md_docx.py`
- `tests/fixtures/ingestao/amostra.txt`
- `tests/fixtures/ingestao/amostra.md`
- `tests/fixtures/ingestao/amostra.docx` (ficheiro mínimo sintético)

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- engine/ingestao/pdf.py, caixas.py, paginas.py (PLN-03)
- engine/ingestao/ocr.py, imagens.py, pdf_ocr.py (PLN-04)
- engine/ingestao/url.py, ssrf.py (PLN-05)
- engine/embeddings/, engine/pesquisa/, engine/juiz/, engine/escalonador/, engine/resposta/, engine/api/, apps/ui/

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

Fixtures sintéticas, frases inventadas. Dois caminhos com o mesmo conteúdo partilham o SHA e continuam a ser dois documentos. A fila regista o documento; o trabalho pesado fica para PLN-06 e PLN-10.

## Requisitos que este PR fecha

- `REQ-ING-001` fecha com `REG-ING-001`.
- `REQ-ING-002` fecha com `REG-ING-002`.
- `REQ-ING-003` fecha com `REG-ING-003`.
- `REQ-ING-004` fecha com `REG-ING-004`.
- `REQ-ING-008` fecha com `REG-ING-008`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/ingestao/test_texto_md_docx.py::test_reg_ing_001`
  - Dado um bloco de texto plano sintético, quando a ingestão é confirmada, então fica um documento com esse texto e entra na fila. Dado um caminho inexistente, quando se pede a extracção, então o erro é tipado e não um traceback genérico.
- `tests/ingestao/test_texto_md_docx.py::test_reg_ing_002`
  - Dado uma amostra Markdown sintética com um título e um parágrafo conhecido, quando se extrai, então o texto contém o parágrafo e a lista de títulos não fica vazia.
- `tests/ingestao/test_texto_md_docx.py::test_reg_ing_003`
  - Dado um .txt UTF-8 e outro com bytes que não são UTF-8, quando se extrai, então o texto legível entra e o fallback documentado não deixa o ficheiro de fora em silêncio.
- `tests/ingestao/test_texto_md_docx.py::test_reg_ing_004`
  - Dado um .docx sintético com parágrafos ordenados, quando se extrai, então o texto plano preserva essa ordem.
- `tests/ingestao/test_hash.py::test_reg_ing_008`
  - Dado um ficheiro acabado de registar, quando se lê o documento, então há um SHA-256 hexadecimal de 64 caracteres dos bytes. Dado esses bytes alterados no disco, quando se volta a verificar, então o estado passa a desactualizado e o índice antigo não é servido como se estivesse actual.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] Este PR não introduz copy de interface.

## Paralelo

Depois deste, PLN-03, PLN-04 e PLN-05 podem avançar em paralelo entre si se cada um só criar os ficheiros seus. PLN-10 pode avançar ao mesmo tempo que este, noutro pacote.
