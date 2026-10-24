# Lente

Chat de pesquisa local com prova na página. Corre no browser em `127.0.0.1:4317`, no mesmo processo que o motor. Windows, macOS e Linux. Alvo: 16 GB de RAM, com ou sem GPU, o mesmo código.

Este repositório, neste marco, contém a **especificação**: o plano aceite, decisões, requisitos, arquitectura, dados, modelos, interface, estrutura futura e planos de implementação. A aplicação ainda não está aqui.

## O que a app faz

Indexa documentos locais (texto, Markdown, docx, PDF, imagem via Tesseract, URL). Procura com EmbeddingGemma 2 (256d) e FTS5 no mesmo SQLite. Um juiz ONNX de 118M decide o highlight. Gemma 4 E2B QAT Q4 escreve a prosa, filtrada por duas portas de citação. Cada frase aceite abre o leitor no trecho literal. Dossier, alertas, lacunas, confronto e feedback só no juiz.

## Modelos

| Papel | Modelo | Notas |
| --- | --- | --- |
| Encontrar | [google/embeddinggemma-2](https://huggingface.co/google/embeddinggemma-2) | Só texto 270M, 256d Matryoshka, residente |
| Decidir | [cross-encoder/mmarco-mMiniLMv2-L12-H384-v1](https://huggingface.co/cross-encoder/mmarco-mMiniLMv2-L12-H384-v1) | ONNX int8 ~119 MB, residente |
| Escrever | [google/gemma-4-E2B-it-qat-q4_0-gguf](https://huggingface.co/google/gemma-4-E2B-it-qat-q4_0-gguf) | ~2,9 GB, visita; BF16 de treino não se descarrega |

Pesos ficam fora deste git. Se o download Hugging Face falhar por licença, a app abre e diz onde pôr o ficheiro.

## Piso da máquina

- Python 3.11+
- Node 22 (só para construir a UI)
- 16 GB de RAM
- Tesseract (única dependência de sistema)
- Um comando sobe UI e motor em `127.0.0.1:4317`

## Mapa deste repositório

| Pasta | Conteúdo |
| --- | --- |
| [docs/origem/](docs/origem/) | Plano aceite (cópia integral do zip de 24–25 out 2026) |
| [docs/LEITURA.md](docs/LEITURA.md) | Como ler IDs, regra de aceitação, decisões de fecho |
| `docs/decisoes/` | ADRs (pull request) |
| `docs/requisitos/` | Requisitos numerados (pull request) |
| `docs/arquitetura/` | Processos, fluxos, orçamento, falhas (pull request) |
| `docs/dados/` | Esquema SQLite e JSON Schema (pull request) |
| `docs/modelos/` | Fichas, prefixos, portas, lentes, confronto (pull request) |
| `docs/interface/` | Chrome, barra, leitor, copy (pull request) |
| `docs/estrutura/` | Árvore futura, módulos, contrato HTTP (pull request) |
| `docs/planos/` | 21 planos de implementação (pull request) |
| `docs/rastreio/` | Matriz origem → requisitos → planos (pull request) |

## Licença

O texto e o código futuros deste repositório: [Apache License 2.0](LICENSE). Os pesos dos modelos seguem as licenças das respectivas fichas Hugging Face; não estão neste repositório.
