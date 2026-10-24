# Ingestão e indexação — `REQ-ING`

## REQ-ING-001

**Enunciado:** A app aceita texto colado como entrada de documento e indexa-o no mesmo fluxo que os ficheiros.

**Origem:** docs/origem/plano.md — «Entradas»

**Critérios de aceitação:**

1. **Dado** uma conversa ou a biblioteca aberta, **quando** o utilizador cola um bloco de texto plain e confirma a ingestão, **então** o texto fica disponível na biblioteca como documento indexável e a pesquisa o encontra após a indexação terminar.

**Não pede:** edição rich-text, anexos mistos na mesma colagem, nem sincronização com a área de transferência em fundo.

---

## REQ-ING-002

**Enunciado:** A app aceita ficheiros Markdown (`.md`) e indexa o conteúdo textual.

**Origem:** docs/origem/plano.md — «Entradas»

**Critérios de aceitação:**

1. **Dado** um ficheiro `.md` válido no disco, **quando** o utilizador o adiciona à biblioteca, **então** o texto do ficheiro é indexado e aparece na lista da biblioteca com o nome do ficheiro.

**Não pede:** pré-visualização renderizada de Markdown na biblioteca, nem execução de HTML embutido no `.md`.

---

## REQ-ING-003

**Enunciado:** A app aceita ficheiros `.txt` e indexa o conteúdo textual.

**Origem:** docs/origem/plano.md — «Entradas»

**Critérios de aceitação:**

1. **Dado** um ficheiro `.txt` com texto legível, **quando** o utilizador o adiciona à biblioteca, **então** o conteúdo é indexado e o documento fica pesquisável após a fila de indexação o processar.

**Não pede:** detecção automática de encoding para todos os charsets possíveis; o comportamento em ficheiros binários mal nomeados pode ser recusa ou aviso explícito.

---

## REQ-ING-004

**Enunciado:** A app aceita ficheiros `.docx` e indexa o texto extraído.

**Origem:** docs/origem/plano.md — «Entradas»

**Critérios de aceitação:**

1. **Dado** um `.docx` com parágrafos de texto, **quando** o utilizador o adiciona à biblioteca, **então** o texto dos parágrafos é extraído, indexado e pesquisável.

**Não pede:** preservação de estilos Word no leitor, macros, comentários ou texto em objectos embutidos não textuais.

---

## REQ-ING-005

**Enunciado:** A app indexa PDFs com camada de texto e grava caixas (bounding boxes) das frases para o highlight no leitor.

**Origem:** docs/origem/plano.md — «Entradas»; fecho de lacuna (LEITURA — «Blocos e frases»)

**Critérios de aceitação:**

1. **Dado** um PDF com texto seleccionável, **quando** a indexação termina, **então** existem frases com offsets e caixas associados às páginas, de modo que um highlight no leitor coincide com o intervalo literal do ficheiro.
2. **Dado** esse PDF indexado, **quando** o utilizador abre o leitor numa citação, **então** a marca aparece sobre o texto da página correcta.

**Não pede:** OCR neste requisito (ver REQ-ING-006); não pede re-extracção a cada abertura do leitor.

---

## REQ-ING-006

**Enunciado:** PDFs digitalizados e imagens passam por Tesseract (única dependência de sistema para OCR) para obter texto indexável.

**Origem:** docs/origem/plano.md — «Entradas»

**Critérios de aceitação:**

1. **Dado** um PDF só imagem ou um ficheiro de imagem suportado, **quando** a indexação corre com Tesseract disponível, **então** é produzido texto indexável e o documento deixa de estar só como binário opaco na biblioteca.
2. **Dado** Tesseract em falta no sistema, **quando** o utilizador tenta indexar um scan, **então** a app mostra um estado de falha ou instrução observável (não falha silenciosa com índice vazio).

**Não pede:** motor OCR alternativo, treino de modelos OCR, nem encoder de visão (ver REQ-FOR-004).

---

## REQ-ING-007

**Enunciado:** A app aceita URL de artigo como entrada e recusa endereços privados.

**Origem:** docs/origem/plano.md — «Entradas»; «Estados vazios»

**Critérios de aceitação:**

1. **Dado** uma URL pública HTTP(S) de artigo alcançável, **quando** o utilizador a submete para ingestão, **então** o conteúdo obtido é indexado como documento de página de URL.
2. **Dado** um endereço privado (ex.: `127.0.0.1`, `10.0.0.0/8`, `192.168.0.0/16`, `169.254.0.0/16`, `::1`, ou hostname que resolva para esses intervalos), **quando** o utilizador o submete, **então** a ingestão é recusada e o estado vazio/aviso de «URL recusada» é mostrado (ver REQ-VAZ-001).

**Não pede:** crawler multi-página, autenticação em sítios remotos, nem proxy configurável.

---

## REQ-ING-008

**Enunciado:** Na ingestão calcula-se SHA-256 dos bytes do ficheiro. Se o ficheiro em disco mudar (hash diferente), a biblioteca marca-o como desactualizado em vez de responder com índice velho em silêncio.

**Origem:** docs/origem/plano.md — «Mais, ainda sem peso»

**Critérios de aceitação:**

1. **Dado** um ficheiro acabado de indexar, **quando** se consulta o registo do documento, **então** existe um SHA-256 gravado correspondente aos bytes indexados.
2. **Dado** esse ficheiro alterado no disco (bytes diferentes), **quando** a app verifica o hash face ao disco, **então** o documento aparece marcado como desactualizado na biblioteca e não se usa o índice antigo como se fosse actual sem aviso.

**Não pede:** reindexação automática imediata sem acção do utilizador; watchers em tempo real em todos os SO.

---

## REQ-ING-009

**Enunciado:** A indexação processa uma fila de um documento de cada vez (um trabalho pesado de ingestão em série).

**Origem:** docs/origem/plano.md — «Entradas»; «Orçamento da máquina»

**Critérios de aceitação:**

1. **Dado** dois ou mais documentos na fila de indexação, **quando** a indexação está a decorrer, **então** só um documento está em processamento activo de indexação de cada vez (o seguinte só começa depois do actual terminar ou ser cancelado de forma explícita).

**Não pede:** paralelismo de indexação multi-documento; priorização sofisticada além da ordem da fila.

---

## REQ-ING-010

**Enunciado:** Na indexação, a unidade de embedding é um bloco de cerca de 500 tokens do tokenizador do EmbeddingGemma, com sobreposição de 50 tokens. A unidade de highlight e de julgamento é a frase, com offsets e caixas gravados. Os títulos extraídos na indexação alimentam o sumário do leitor.

**Origem:** fecho de lacuna (LEITURA — «Blocos e frases»); docs/origem/plano.md — «Entradas»; «O chat e o leitor» (sumário)

**Critérios de aceitação:**

1. **Dado** um documento longo indexado, **quando** se inspeccionam os blocos embutidos, **então** cada bloco tem cerca de 500 tokens (tokenizador EmbeddingGemma) e blocos consecutivos partilham sobreposição de 50 tokens.
2. **Dado** o mesmo documento, **quando** se inspeccionam as unidades de highlight, **então** cada frase tem offsets (e caixas, quando aplicável ao formato) gravados na ingestão.
3. **Dado** um documento com títulos estruturados, **quando** o leitor abre o sumário, **então** lista os títulos extraídos na indexação.

**Não pede:** re-tokenização na procura; sumário gerado por LLM; caixas em formatos sem geometria de página.

---

## REQ-ING-011

**Enunciado:** As miniaturas do leque são imagens pequenas feitas uma vez na indexação (não um PDF renderizado ao passar o rato). Se a licença Hugging Face bloquear um download de modelo, a app abre e indica onde pôr o ficheiro.

**Origem:** docs/origem/plano.md — «Orçamento da máquina»; «Como corre»

**Critérios de aceitação:**

1. **Dado** um documento indexado com pelo menos uma página visualizável, **quando** a indexação termina, **então** existe miniatura persistida associada ao documento/página, reutilizada no leque sem re-renderizar o PDF no hover.
2. **Dado** um download de pesos bloqueado por licença Hugging Face, **quando** a app inicia, **então** a interface abre e mostra uma mensagem que indica o caminho ou local onde o utilizador deve colocar o ficheiro do modelo.

**Não pede:** galeria de miniaturas por todas as páginas na biblioteca; contorno automático da licença HF; download dos 11 GB de pesos de treino do E2B.
