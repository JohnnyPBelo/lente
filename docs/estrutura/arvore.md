# Árvore futura

Árvore-alvo do repositório e do runtime. **Nenhum destes caminhos de código é criado por esta especificação** — só documenta o destino.

```
apps/ui/          # Node 22, React, shadcn — build output served by engine
engine/           # Python 3.11+
  ingestao/
  indice/
  pesquisa/
  juiz/
  escritor/
  escalonador/
  armazenamento/
  api/            # HTTP on 127.0.0.1:4317
data/             # runtime only, gitignored
models/           # runtime weights, gitignored
docs/             # this specification
```

## `apps/ui/`

Interface React (Node 22, shadcn/ui reestilizado). Constrói artefacto estático. O motor serve esse artefacto em `127.0.0.1:4317`. Não corre um servidor de desenvolvimento como processo permanente da app.

Responsável pelo chrome em vidro, barra de escrita, chat, leque, leitor, barra lateral e estados vazios. Fala com o motor só via HTTP local.

## `engine/`

Motor Python 3.11+. Um processo. Carrega modelos conforme o orçamento (EmbeddingGemma e juiz residentes; E2B visita). Pausa indexação e treino quando há procura.

### `engine/ingestao/`

Entra ficheiro ou URL; sai texto, frases com offsets e caixas, SHA-256, blocos ~500 tokens. PDF, texto, Markdown, `.docx`, imagem/OCR (Tesseract), URL com recusa de endereços privados.

### `engine/indice/`

Escreve no SQLite: documentos, FTS5, vectores `sqlite-vec`, miniaturas, sumário de títulos. Uma fila de um documento. Marca desactualizado se o hash em disco mudar.

### `engine/pesquisa/`

Fusão FTS5 + cosseno exacto (embedding 256-d). Prefixos EmbeddingGemma por lente. Candidatos para o juiz. Modos: procurar, correlacionar, lacunas (sem E2B). Identificador literal fura o chão de cosseno.

### `engine/juiz/`

Cross-encoder ONNX int8 residente. Decide highlight e as duas portas da prosa. Confronto determinístico (duas direcções + cosseno). Feedback e LoRA quando a máquina está livre. Não escreve prosa.

### `engine/escritor/`

Gemma 4 E2B QAT Q4: sobe, escreve, desce. Só vê trechos desta procura (+ página aberta se a pergunta for sobre ela). Frases só saem depois de `[n]` e do juiz. Alertas e lacunas não o chamam.

### `engine/escalonador/`

Um trabalho pesado de cada vez. Pausa/retoma indexação e treino. Reserva núcleos para UI e sistema. Limita o E2B aos núcleos de escrita.

### `engine/armazenamento/`

Um SQLite em `data/`: documentos, vectores, FTS5, chats, feedback, dossiers, alertas, diário, etiquetas. Sem base vectorial à parte. Cópia de segurança = zip de `data/`.

### `engine/api/`

HTTP só em `127.0.0.1:4317`. Serve a UI construída e os endpoints do [contrato-http.md](contrato-http.md). Sem rede pública, contas ou sync.

## `data/`

Runtime. Gitignored. SQLite, diário append-only, estado de filas. Uma cópia do ficheiro SQLite leva o índice.

## `models/`

Runtime. Gitignored. Pesos: EmbeddingGemma 2 (~2 GB), juiz ONNX (~0,5 GB / ~120 MB int8), E2B Q4 (~3 GB). Se o download Hugging Face falhar, a app abre e indica onde pôr o ficheiro.

## `docs/`

Esta especificação (origem, leitura, estrutura, e o resto da ordem em [LEITURA.md](../LEITURA.md)). Não é código de execução.
