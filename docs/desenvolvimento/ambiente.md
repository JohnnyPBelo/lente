# Ambiente

Piso do produto: Python 3.11+, Node 22, 16 GB de RAM, Tesseract como única dependência de sistema. Windows, macOS e Linux. GPU, se existir, acelera o mesmo código.

## Ferramentas

| Peça | Uso | Notas |
| --- | --- | --- |
| Python 3.11+ | Motor | Um processo. Serve a UI já construída em `127.0.0.1:4317`. |
| Node 22 | Construir `apps/ui` | Não fica a correr como servidor da app. |
| Tesseract | OCR de PDF digitalizado e imagem | Pacote de língua `por`. É a única dependência de sistema. |
| pytest | Testes do motor | Um directório `tests/` na raiz, espelhando os pacotes. |
| Vitest | Testes da UI (`*.test.tsx`) | A partir do PLN-13. |
| sentence-transformers | EmbeddingGemma 2 | Carga só de texto: `vision_config=None`, `audio_config=None`. Corte 256 e `normalize_embeddings=True`. |
| onnxruntime | Juiz | Ficheiro int8: `onnx/model_qint8_avx512_vnni.onnx`, ou `model_qint8_arm64.onnx` em arm64. |
| llama-cpp-python | E2B GGUF | Runtime local do Q4_0. Sobe para a resposta e desce a seguir. |

Bibliotecas de PDF, docx e HTTP ficam dentro do processo Python. Pandoc não entra: Tesseract continua a ser a única dependência de sistema.

## Layout no disco da máquina, fora do git

```
models/embeddinggemma-2/     # texto 270M; tecto ~2 GB
models/juiz/                 # ONNX int8 ~119 MB + tokenizador; tecto com PyTorch base ~0,5 GB
models/e2b/                  # gemma-4-E2B-it-qat-q4_0-gguf, ~2,9 GB
data/lente.sqlite            # um ficheiro: documentos, FTS5, vectores, chats, dossiers
```

Os três tectos são os do plano. Os nomes das pastas são os que o código de [PLN-21](../planos/PLN-21-estados-vazios-a11y-e-comando-unico.md) deve procurar. Se o Hugging Face recusar o download, a app abre na mesma e mostra este caminho.

Não descarregar:

- Pesos BF16 / unquantized de treino do E2B (~11,4 GB).
- Encoders de visão e de áudio do EmbeddingGemma.
- Qualquer checkpoint que não seja o ONNX int8 do juiz, excepto o PyTorch base desse mesmo modelo de 118M, e só quando houver LoRA para treinar.

## Variáveis

Não há contas. Um ficheiro local, gitignored, pode apontar o token Hugging Face para o primeiro download. O token não se commita. A app tem de arrancar sem token se os três directórios de pesos já estiverem preenchidos, e também sem o E2B (excertos e miniaturas).

## O que um teste não pode fazer

- Ligar a `0.0.0.0` ou a um host que não seja loopback.
- Descarregar pesos durante a suite por omissão. Testes de carga de modelo ficam marcados e usam um double, salvo o teste que verifica o caminho do ficheiro em falta.
- Escrever em `data/` ou `models/` do programador. Cada teste recebe um directório temporário.
