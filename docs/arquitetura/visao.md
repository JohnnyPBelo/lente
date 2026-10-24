# Visão geral

## Um só servidor

A Lente corre como **uma** aplicação de secretária no browser local.

| Elemento | Valor verificável |
| --- | --- |
| Endereço | `127.0.0.1:4317` |
| Quem escuta | Motor Python (processo único de runtime) |
| O que serve | UI já construída (estáticos) + API do motor |
| Quem não escuta em produção | Node 22 (só constrói a UI) |
| Empacotamento | Sem Electron |

Um comando sobe o motor; o browser abre `http://127.0.0.1:4317`. Não há segundo processo de UI em runtime. Decisão de fecho em [docs/LEITURA.md](../LEITURA.md): «Um só servidor».

## Três papéis de modelo

| Papel | Modelo | Residência | Função |
| --- | --- | --- | --- |
| Encontrar | EmbeddingGemma 2 (270M, só texto), vector 256-d (Matryoshka a partir de 768), float32 em CPU | Residente | Embedding de blocos e de consultas |
| Decidir highlight | Cross-encoder `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` (118M), ONNX int8 (~120 MB) | Residente | Pontua frase↔trecho; filtra highlights e prosa |
| Escrever | Gemma 4 E2B QAT Q4 | Visita: sobe para a resposta, desce a seguir | Prosa citada; nunca fine-tuned nem com respostas anteriores no prompt |

Não há System One Jev local. Não se carregam visão nem áudio do EmbeddingGemma. O PyTorch do juiz só entra para treino LoRA e sai da memória no fim.

## Dois residentes, um visitante

Numa procura típica ficam carregados: sistema, browser, EmbeddingGemma float32, juiz ONNX int8, SQLite. O E2B **não** é residente. Sem o E2B disponível, o chat continua com excertos e miniaturas (ver [falhas.md](falhas.md)).

## Persistência: um ficheiro SQLite

Tudo o que precisa de sobreviver a reinícios vive no mesmo SQLite em `data/`:

- documentos, hashes SHA-256, FTS5
- vectores via extensão `sqlite-vec` (mesmo processo, mesmo ficheiro)
- chats, feedback, dossiers (fotografia no fecho), alertas, diário

Não há base vectorial à parte (Qdrant, Chroma, LanceDB, Postgres). A pesquisa é **cosseno exacto** sobre os vectores guardados; não se usa índice aproximado (incluindo Vec1 oficial pré-1.0).

Uma cópia do ficheiro SQLite leva o índice consigo. A cópia de segurança da app é a pasta `data/` num zip.

## Fusão de pesquisa

1. FTS5 → candidatos por termo exacto (CVE, cláusula, sigla).
2. Embedding + cosseno exacto → candidatos semânticos.
3. Fusão por rank recíproco no código.
4. Juiz ONNX filtra o que se marca e o que passa nas duas portas da prosa.

Identificadores literais furam o chão de cosseno; continuam sujeitos ao juiz.

## Duas portas da prosa

Antes de uma frase aparecer no fio:

1. Termina com `[n]` de um trecho do pacote desta procura.
2. O juiz confirma fidelidade frase↔trecho citado.

Se nenhuma frase sobreviver: excertos + miniaturas, ou aviso de vazio. Miniaturas podem aparecer primeiro; prosa filtrada nunca se mostra a ser apagada.

## Superfície verificável

- Biblioteca: PDF, texto, Markdown, `.docx`, URL de artigo (recusa de endereços privados), OCR via Tesseract.
- Barra única: procurar, correlacionar, confrontar, alerta, lacunas; lente à parte (não muda o confronto).
- Leitor: highlight = intervalo literal do ficheiro (offsets/caixas da ingestão).
- Dossier: fotografia sem voltar a correr modelos; SHA-256 do ficheiro no fecho.
