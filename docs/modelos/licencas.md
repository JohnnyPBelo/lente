# MOD-lic — Licenças: repositório vs pesos

## Repositório Lente

| Âmbito | Licença |
| --- | --- |
| Texto da especificação e código futuros neste git | **Apache License 2.0** — ficheiro [`LICENSE`](../../LICENSE) na raiz |

Isto cobre documentação e código da aplicação. **Não** inclui binários de modelos.

## Pesos dos modelos (fora do git)

Os pesos **não** estão neste repositório (`.gitignore` / política de download). Cada um permanece sob a licença da respectiva ficha Hugging Face:

| Modelo | Ficha | Nota de licença (ficha) |
| --- | --- | --- |
| EmbeddingGemma 2 | [google/embeddinggemma-2](https://huggingface.co/google/embeddinggemma-2) | **Apache 2.0** — a ficha/documentação permite afinar e implantar; ver também [embeddinggemma.md](embeddinggemma.md) |
| Juiz mmarco | [cross-encoder/mmarco-mMiniLMv2-L12-H384-v1](https://huggingface.co/cross-encoder/mmarco-mMiniLMv2-L12-H384-v1) | **Apache 2.0** |
| E2B QAT Q4 GGUF | [google/gemma-4-E2B-it-qat-q4_0-gguf](https://huggingface.co/google/gemma-4-E2B-it-qat-q4_0-gguf) | Licença **Gemma 4** conforme a ficha ([ligação oficial](https://ai.google.dev/gemma/docs/gemma_4_license)); distinta do acto de publicar código Apache-2.0 no repo Lente |

O Apache-2.0 do Lente **não** redistribui nem «relicencia» os pesos. A app descarrega-os para disco local do utilizador, ou indica o caminho se o Hub bloquear o download por termos.

## O que não vai para o git

- Ficheiros `.gguf`, ONNX de modelos, safetensors, checkpoints BF16 (~11,4 GB do E2B), adaptadores LoRA binários.
- Qualquer cópia dos pesos sob `data/` ou cache de modelos.

O que se partilha entre instalações, quando o utilizador exporta afinações, é o **JSON de correcções** (texto de trechos + etiquetas), não o binário LoRA — ver plano «Juntar afinações».

## Aceitação

1. **Dado** um clone limpo do repositório, **quando** se listam os ficheiros versionados, **então** não há pesos EmbeddingGemma, juiz ONNX nem GGUF E2B.
2. **Dado** a documentação de licenças, **quando** se lê este contrato, **então** fica explícito que o Apache-2.0 do repo cobre texto/código e que os pesos seguem as fichas HF.

## Origem

[`README.md`](../../README.md) na raiz; [docs/origem/plano.md](../origem/plano.md) — orçamento e download; fichas Hugging Face dos três modelos.
