# Contratos dos modelos — Lente

Contratos derivados de [docs/origem/plano.md](../origem/plano.md) e das decisões de fecho em [docs/LEITURA.md](../LEITURA.md). Cada ficha fecha IDs `MOD-…`: o que carrega, em que dtype, que prefixos, que limiares e o que fica de fora.

Os pesos **não** entram neste repositório. Licenças: [licencas.md](licencas.md).

## Índice

| Ficheiro | ID | Conteúdo |
| --- | --- | --- |
| [embeddinggemma.md](embeddinggemma.md) | `MOD-emb` | EmbeddingGemma 2 só texto, 256d, dtypes, prefixos |
| [juiz.md](juiz.md) | `MOD-juiz` | Cross-encoder ONNX int8, porta de highlight, LoRA |
| [e2b.md](e2b.md) | `MOD-e2b` | Gemma 4 E2B QAT Q4 GGUF, visita, congelado |
| [prefixos-e-lentes.md](prefixos-e-lentes.md) | `MOD-lentes` | Lente → prefixo; prosa E2B; alerta/lacunas sem E2B |
| [duas-portas.md](duas-portas.md) | `MOD-portas` | Porta `[n]` + fidelidade; sem prosa provisória |
| [fusao-limiar-platt.md](fusao-limiar-platt.md) | `MOD-fusao` | RRF, limiar visível, Platt após correcções |
| [confronto.md](confronto.md) | `MOD-confronto` | Regra determinística + limiares + exemplos sintéticos |
| [licencas.md](licencas.md) | `MOD-lic` | Repo Apache-2.0 vs licenças HF dos pesos |

## Três papéis (resumo)

| Papel | Modelo | Residência |
| --- | --- | --- |
| Encontrar | [google/embeddinggemma-2](https://huggingface.co/google/embeddinggemma-2) | Residente |
| Decidir highlight | [cross-encoder/mmarco-mMiniLMv2-L12-H384-v1](https://huggingface.co/cross-encoder/mmarco-mMiniLMv2-L12-H384-v1) | Residente (ONNX int8) |
| Escrever | [google/gemma-4-E2B-it-qat-q4_0-gguf](https://huggingface.co/google/gemma-4-E2B-it-qat-q4_0-gguf) | Visita |

## Convenções

- Português de Portugal.
- Números e limiares são parte do contrato: testes de aceitação usam estes valores até um ADR os alterar.
- Exemplos de trechos são sintéticos; não copiam documentos reais nem pesos.
