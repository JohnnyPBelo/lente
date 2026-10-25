# Ordem de trabalho PLN-03

Fonte: `docs/planos/PLN-03-pdf-com-texto-e-caixas.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Extrair de PDF com camada de texto: texto por página, offsets, e caixas bounding-box por span/frase, suficientes para o leitor pintar highlights literais.

## Fronteira

o que NÃO entra neste plano — OCR de scans (PLN-04), embeddings, miniaturas finais (podem stub), UI do leitor.

## Teste que falha primeiro, no plano

`tests/ingestao/test_pdf_texto_caixas.py` — `extrair_pdf(fixture)` devolve ≥1 página; o texto contém a frase fixture; existe pelo menos uma caixa com `pagina==1` e largura/altura > 0 alinhada a um span dessa frase.

Nesta ordem esse teste é `test_reg_ing_005`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-01
- PLN-02

## Ficheiros que este PR pode criar

- `engine/ingestao/pdf.py`
- `engine/ingestao/caixas.py` — modelo `{pagina, x, y, largura, altura}` e serialização JSON
- `engine/ingestao/paginas.py` — estrutura comum `PaginaExtraida` (texto, spans)
- `tests/ingestao/test_pdf_texto_caixas.py`
- `tests/fixtures/ingestao/amostra_texto.pdf` — PDF sintético com texto seleccionável

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- engine/ingestao/texto.py, markdown.py, docx.py, hash.py (PLN-02): importar, não reescrever
- engine/ingestao/ocr.py, imagens.py, pdf_ocr.py (PLN-04)
- engine/ingestao/url.py, ssrf.py (PLN-05)
- engine/embeddings/, engine/pesquisa/, apps/ui/, o leitor

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

A biblioteca de PDF fica declarada e a licença cabe na mensagem do commit de dependência. Quem pinta o highlight é a UI; aqui grava-se o intervalo literal e as caixas.

## Requisitos que este PR fecha

- `REQ-ING-005` fecha com `REG-ING-005`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `tests/ingestao/test_pdf_texto_caixas.py::test_reg_ing_005`
  - Dado um PDF sintético com texto seleccionável, quando se extrai, então há pelo menos uma página, a frase da fixture, e uma caixa na página 1 com largura e altura maiores que zero. Dado um PDF só com imagem, então precisa_ocr fica verdadeiro e o Tesseract não é chamado. Dado várias páginas, então cada caixa traz o número de página certo.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] Este PR não introduz copy de interface.

## Paralelo

Pode avançar ao lado de PLN-05 e de PLN-10. PLN-04 espera por este por causa de precisa_ocr. Não avançar ao lado de quem edite registo.py ao mesmo tempo sem rebase.
