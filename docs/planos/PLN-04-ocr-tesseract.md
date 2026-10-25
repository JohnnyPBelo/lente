# PLN-04: OCR (Tesseract)

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Quando o PDF ou a imagem não têm texto seleccionável, correr Tesseract (única dependência de sistema) e produzir texto + caixas aproximadas por palavra/linha para indexação e highlight.
**Fronteira:** o que NÃO entra neste plano — encoder de visão, modelos de OCR neurais, UI; não substituir extracção nativa de PDF com texto (PLN-03).
**Ficheiros futuros:**
- `engine/ingestao/ocr.py`
- `engine/ingestao/imagens.py` — PNG/JPEG/WebP → raster para OCR
- `engine/ingestao/pdf_ocr.py` — render página → OCR quando `precisa_ocr`
- `tests/ingestao/test_ocr.py`
- `tests/fixtures/ingestao/amostra_scan.png` — imagem sintética com texto legível
**Teste que falha primeiro:** `tests/ingestao/test_ocr.py` — com Tesseract instalado, `ocr_imagem(fixture)` devolve texto que contém a palavra fixture (ex. `LENTE`) e pelo menos uma caixa com dimensões positivas; se Tesseract ausente, o teste salta com mensagem clara ou falha com erro tipado `TesseractEmFalta` documentado.

## Passos

- [ ] Documentar no README do motor: instalar Tesseract + idioma `por` (e `eng` se necessário).
- [ ] Escrever teste que falha / skip condicional bem definido.
- [ ] Commit: `test(ingestao): falha sem OCR Tesseract`.
- [ ] Implementar wrapper: comando ou `pytesseract`; timeout; captura de stderr.
- [ ] Mapear TSV/box output → `caixas_json` no mesmo formato do PLN-03.
- [ ] Pipeline: se PDF `precisa_ocr`, OCR página a página; gravar `paginas` e texto.
- [ ] Fazer o teste passar em CI com Tesseract ou marcar job opcional documentado.
- [ ] Commit: `feat(ingestao): OCR Tesseract para scans e imagens`.
- [ ] Teste: imagem sem texto → string vazia / estado `erro` ou `ok` com aviso — escolher e fixar comportamento observável.
- [ ] Teste: não chamar OCR quando PLN-03 já extraiu texto.
- [ ] Commit: `test(ingestao): OCR só quando necessário`.
- [ ] Commit de fecho.

## Notas para o executor

- Idioma por omissão: português (`por`); configurável mais tarde.
- Orçamento: OCR é trabalho pesado de indexação — respeitará o escalonador (PLN-10); neste plano pode correr síncrono nos testes.
