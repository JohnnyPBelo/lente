# Ordem de trabalho PLN-04

Fonte: `docs/planos/PLN-04-ocr-tesseract.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Quando o PDF ou a imagem não têm texto seleccionável, correr Tesseract (única dependência de sistema) e produzir texto + caixas aproximadas por palavra/linha para indexação e highlight.

## Fronteira

o que NÃO entra neste plano — encoder de visão, modelos de OCR neurais, UI; não substituir extracção nativa de PDF com texto (PLN-03).

## Teste que falha primeiro, no plano

`tests/ingestao/test_ocr.py` — com Tesseract instalado, `ocr_imagem(fixture)` devolve texto que contém a palavra fixture (ex. `LENTE`) e pelo menos uma caixa com dimensões positivas; se Tesseract ausente, o teste salta com mensagem clara ou falha com erro tipado `TesseractEmFalta` documentado.

Nesta ordem esse teste é `test_reg_ing_006`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-01
- PLN-02
- PLN-03

## Ficheiros que este PR pode criar

- `engine/ingestao/ocr.py`
- `engine/ingestao/imagens.py` — PNG/JPEG/WebP → raster para OCR
- `engine/ingestao/pdf_ocr.py` — render página → OCR quando `precisa_ocr`
- `tests/ingestao/test_ocr.py`
- `tests/fixtures/ingestao/amostra_scan.png` — imagem sintética com texto legível

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- engine/ingestao/pdf.py e caixas.py (PLN-03): ler precisa_ocr, não substituir a extracção com texto
- engine/ingestao/url.py, ssrf.py (PLN-05)
- engine/embeddings/, apps/ui/, qualquer encoder de visão

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

Idioma por omissão: por. Sem Tesseract o teste afirma TesseractEmFalta. Com Tesseract afirma a palavra LENTE. Para o caso positivo passar no GitHub Actions, este PR pode instalar tesseract-ocr e tesseract-ocr-por no job regressao. Não muda os gatilhos do workflow e não descarrega modelos. Skip não conta como teste.

## Requisitos que este PR fecha

- `REQ-ING-006` fecha com `REG-ING-006`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/ingestao/test_ocr.py::test_reg_ing_006`
  - Dado uma imagem sintética com a palavra LENTE e o Tesseract instalado, quando corre o OCR, então o texto contém LENTE e há uma caixa com dimensões positivas. Dado o binário em falta, então o erro tipado é TesseractEmFalta e não um índice vazio em silêncio. Dado um PDF que já tem texto, então o OCR não corre. O CI deste PR instala tesseract-ocr e a língua por para o caso positivo poder passar sem skip.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] Este PR não introduz copy de interface.

## Paralelo

Pode avançar ao lado de PLN-05 e de PLN-10, depois de PLN-03. Não cria url.py nem reescreve o extractor de PDF com texto.
