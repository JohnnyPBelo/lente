# PLN-03: PDF com texto e caixas

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Extrair de PDF com camada de texto: texto por página, offsets, e caixas bounding-box por span/frase, suficientes para o leitor pintar highlights literais.
**Fronteira:** o que NÃO entra neste plano — OCR de scans (PLN-04), embeddings, miniaturas finais (podem stub), UI do leitor.
**Ficheiros futuros:**
- `engine/ingestao/pdf.py`
- `engine/ingestao/caixas.py` — modelo `{pagina, x, y, largura, altura}` e serialização JSON
- `engine/ingestao/paginas.py` — estrutura comum `PaginaExtraida` (texto, spans)
- `tests/ingestao/test_pdf_texto_caixas.py`
- `tests/fixtures/ingestao/amostra_texto.pdf` — PDF sintético com texto seleccionável
**Teste que falha primeiro:** `tests/ingestao/test_pdf_texto_caixas.py` — `extrair_pdf(fixture)` devolve ≥1 página; o texto contém a frase fixture; existe pelo menos uma caixa com `pagina==1` e largura/altura > 0 alinhada a um span dessa frase.

## Passos

- [ ] Gerar fixture PDF mínimo (ferramenta de build de teste ou commit binário pequeno sintético).
- [ ] Escrever o teste que falha (texto + caixas).
- [ ] Commit: `test(ingestao): falha sem extractor PDF com caixas`.
- [ ] Escolher biblioteca PDF (ex. pypdf / pymupdf) e documentar licença no commit/mensagem de dependência.
- [ ] Implementar extracção por página; coordenadas num sistema documentado (origem, unidades); `caixas_json` compatível com o esquema de `frases`.
- [ ] Mapear spans → candidatos a frase (separação por pontuação); offsets no texto concatenado da página ou do documento — fixar uma convenção e testá-la.
- [ ] Fazer o teste passar.
- [ ] Commit: `feat(ingestao): PDF com texto e caixas`.
- [ ] Teste: PDF sem texto (só imagem) → resultado vazio/flag `precisa_ocr=True` (sem chamar Tesseract ainda).
- [ ] Teste: documento de várias páginas — `pagina` correcto em cada caixa.
- [ ] Integrar com `registo.py` (PLN-02): PDF entra na biblioteca com `paginas` preenchido.
- [ ] Commit: `test(ingestao): PDF multipágina e detecção sem texto`.
- [ ] Commit de fecho.

## Notas para o executor

- Miniaturas: se geradas aqui, devem ser imagens pequenas estáticas; não renderizar PDF no hover (plano de origem). Pode adiar geração real para um passo no fim deste plano ou no início do PLN-06.
- Quem pinta o highlight é o código da UI; aqui só se grava o intervalo literal e as caixas.
