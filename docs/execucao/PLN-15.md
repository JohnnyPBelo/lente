# Ordem de trabalho PLN-15

Fonte: `docs/planos/PLN-15-leque-e-leitor.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Após resposta com documentos: miniaturas; um doc abre leitor; vários abrem leque → escolha → cresce até leitor; Escape/minimizar recolhe; leitor com scroll contínuo, highlights literais, zoom, sumário, cópia de citação, fixar trecho; serif no texto; `prefers-reduced-motion` encurta sem remover leque/leitor.

## Fronteira

o que NÃO entra neste plano — dossier (PLN-18), feedback LoRA (PLN-16), OCR novo.

## Teste que falha primeiro, no plano

`Leque.test.tsx` — com 3 miniaturas, hover/foco (desktop) revela leque; click na 2.ª chama `onAbrir(docId)`; com `prefers-reduced-motion: reduce`, animações curtas/ausentes mas leque e abertura permanecem disponíveis.

Nesta ordem esse teste é `reg-cht-004.test.tsx`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-13

## Ficheiros que este PR pode criar

- `apps/ui/src/components/leque/Leque.tsx`
- `apps/ui/src/components/leque/Miniatura.tsx`
- `apps/ui/src/components/leitor/Leitor.tsx`
- `apps/ui/src/components/leitor/Highlights.tsx`
- `apps/ui/src/components/leitor/Sumario.tsx`
- `apps/ui/src/components/leitor/Ferramentas.tsx` — zoom, página, procurar neste doc
- `apps/ui/src/components/chat/CitacaoLink.tsx` — clique → leitor na página/highlight
- `engine/api/rotas_documento.py` — bytes/páginas/sumário/miniatura
- `tests` UI: `Leque.test.tsx`, `Leitor.highlights.test.tsx`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- apps/ui/src/components/barra/ (PLN-14) e o chrome de PLN-13, incluindo App.tsx
- engine/api/rotas_chat.py e rotas_modos.py. Este PR só cria rotas_documento.py e o fixar trecho se ainda não existir
- engine/dossier/ (PLN-18) e engine/feedback/lora.py (PLN-16)

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

Rotas: HTTP-reader-document, HTTP-reader-pages, HTTP-reader-highlights e HTTP-chat-pin-excerpt. Miniaturas vindas da indexação. Highlight é intervalo literal. Copy do leitor em docs/interface/copy.md e docs/interface/leitor.md.

## Requisitos que este PR fecha

- `REQ-BUS-011` fecha com `REG-BUS-011`.
- `REQ-JUI-003` fecha com `REG-JUI-003`.
- `REQ-RES-009` fecha com `REG-RES-009`.
- `REQ-CHT-003` fecha com `REG-CHT-003`.
- `REQ-CHT-004` fecha com `REG-CHT-004`.
- `REQ-CHT-005` fecha com `REG-CHT-005`.
- `REQ-CHT-006` fecha com `REG-CHT-006`.
- `REQ-CHT-007` fecha com `REG-CHT-007`.
- `REQ-CHT-008` fecha com `REG-CHT-008`.
- `REQ-LEI-001` fecha com `REG-LEI-001`.
- `REQ-LEI-002` fecha com `REG-LEI-002`.
- `REQ-LEI-003` fecha com `REG-LEI-003`.
- `REQ-LEI-004` fecha com `REG-LEI-004`.
- `REQ-LEI-005` fecha com `REG-LEI-005`.
- `REQ-LEI-006` fecha com `REG-LEI-006`.
- `REQ-LEI-007` fecha com `REG-LEI-007`.
- `REQ-LEI-008` fecha com `REG-LEI-008`.
- `REQ-LEI-009` fecha com `REG-LEI-009`.
- `REQ-LEI-010` fecha com `REG-LEI-010`.
- `REQ-LEI-011` fecha com `REG-LEI-011`.
- `REQ-DOS-001` fecha com `REG-DOS-001`.
- `REQ-DOS-002` fecha com `REG-DOS-002`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `apps/ui/src/components/chat/reg-bus-011.test.tsx`
  - Dado Conceito A e Conceito B enviados, quando a mensagem aparece, então há três cores para A, B e a relação, com as legendas de copy.md, e as miniaturas entram no leque dessa mensagem.
- `apps/ui/src/components/leitor/reg-jui-003.test.tsx`
  - Dado uma frase deixada passar pelo juiz, quando o highlight se pinta, então a marca é o intervalo literal dos offsets e das caixas gravados na ingestão, não texto regenerado.
- `apps/ui/src/components/chat/reg-res-009.test.tsx`
  - Dado uma frase que passou as duas portas, quando se clica a citação, então o destino é a página e o highlight desse número, com documento e offsets.
- `apps/ui/src/components/leque/reg-cht-003.test.tsx`
  - Dado highlights em um ou mais documentos, quando a mensagem se mostra, então cada documento tem uma miniatura da página do primeiro highlight, feita na indexação e não um PDF renderizado no hover.
- `apps/ui/src/components/leque/reg-cht-004.test.tsx`
  - Dado um só documento, quando se clica a miniatura, então abre o leitor. Dado três miniaturas, quando há hover ou foco, então aparece o leque e o clique na segunda chama a abertura com o id dessa.
- `apps/ui/src/components/leitor/reg-cht-005.test.tsx`
  - Dado o leitor aberto a partir de uma mensagem, quando se minimiza ou se prime Escape, então recolhe à miniatura e o chat fica no mesmo sítio.
- `apps/ui/src/components/leque/reg-cht-006.test.tsx`
  - Dado vários documentos em tacto, quando o primeiro toque chega ao conjunto, então abre o leque. Quando o segundo toque escolhe uma miniatura, então abre o leitor nesse documento.
- `apps/ui/src/components/leque/reg-cht-007.test.tsx`
  - Dado prefers-reduced-motion reduce, quando se abre o leque, então a animação encurta e o leque e a abertura do leitor continuam disponíveis.
- `apps/ui/src/components/leitor/reg-cht-008.test.tsx`
  - Dado uma resposta com documentos, quando a mensagem entra, as miniaturas aparecem, o leque abre, o leitor cresce, o highlight acende e o leitor recolhe, então cada momento tem animação curta, salvo reduced motion. O chrome está em português, com vidro e Geist; a superfície de leitura usa serif.
- `apps/ui/src/components/leitor/reg-lei-001.test.tsx`
  - Dado um documento de cada tipo suportado, PDF, texto, Markdown, página de URL e imagem, quando se abre no leitor, então o documento inteiro é navegável e não só o excerto da citação.
- `apps/ui/src/components/leitor/reg-lei-002.test.tsx`
  - Dado um documento com várias páginas e vários highlights, quando o leitor está aberto, então o scroll é contínuo, as marcas aparecem nas páginas atingidas e dá para saltar entre elas.
- `apps/ui/src/components/leitor/reg-lei-003.test.tsx`
  - Dado o leitor, quando se usa zoom, ajustar à largura e ajustar à página, então a vista muda. Dado uma imagem ou um scan, quando se arrasta, então o conteúdo desloca-se.
- `apps/ui/src/components/leitor/reg-lei-004.test.tsx`
  - Dado um documento paginado, quando se indica um número de página, então o leitor vai a essa página. Dado um termo presente, quando se procura neste documento, então a ocorrência aparece.
- `apps/ui/src/components/leitor/reg-lei-005.test.tsx`
  - Dado títulos extraídos na indexação, quando se abre o sumário, então a lista é essa e escolher um título navega para a secção.
- `apps/ui/src/components/leitor/reg-lei-006.test.tsx`
  - Dado texto seleccionado, quando se copia, então esse texto fica disponível. Dado copiar a citação, então o resultado inclui ficheiro e página no formato indicado em copy.md.
- `apps/ui/src/components/leitor/reg-lei-007.test.tsx`
  - Dado o fluxo Corrigir activo, quando se selecciona texto no leitor, então o pedido leva essa selecção como trecho positivo e as marcas da resposta como negativas.
- `tests/api/test_fixar_trecho.py::test_reg_lei_008`
  - Dado um trecho fixado a partir do leitor, quando a acção conclui, então existe uma linha no SQLite. Dado o mesmo chat reaberto, então o trecho continua acessível sem nova procura.
- `apps/ui/src/components/leitor/reg-lei-009.test.tsx`
  - Dado o leitor aberto, quando se compara a área de texto com o chrome, então o texto assenta numa superfície sólida com serif e o chrome continua em vidro.
- `apps/ui/src/components/leitor/reg-lei-010.test.tsx`
  - Dado texto seleccionado no leitor, quando se activa a bolha Confrontar, então o primeiro lugar vazio fica preenchido com essa selecção e o foco volta à barra para o segundo lugar.
- `apps/ui/src/components/leitor/reg-lei-011.test.tsx`
  - Dado a abertura do leitor a partir de uma citação, quando a página chega, então o highlight acende uma vez. Dado minimizar ou Escape, então regressa à miniatura no mesmo sítio do chat.
- `apps/ui/src/components/chat/reg-dos-001.test.tsx`
  - Dado frases que passaram as duas portas, quando se vê o fio, então cada uma é um link activável e não texto morto.
- `apps/ui/src/components/chat/reg-dos-002.test.tsx`
  - Dado uma citação no fio, quando se clica, então o leitor abre nessa página e nesse highlight sem obrigar a passar pelo leque. Dado vários documentos, então o leque continua disponível para escolher à mão.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] O texto visível vem de `docs/interface/copy.md`, sem frase inventada para o mesmo estado.

## Paralelo

Pode avançar ao lado de PLN-14 nas condições desse plano, e ao lado de PLN-16, PLN-18 e PLN-19 se cada um ficar nos seus componentes.
