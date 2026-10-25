# Lente

Chat de pesquisa local com prova na página. Corre no browser em `127.0.0.1:4317`, no mesmo processo que o motor. Windows, macOS e Linux. Alvo: 16 GB de RAM, com ou sem GPU, o mesmo código.

Este repositório contém a especificação completa no ramo `main`. A aplicação ainda não está aqui. Quem for implementar começa por [docs/desenvolvimento/](docs/desenvolvimento/).

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
| [docs/decisoes/](docs/decisoes/) | ADRs aceites |
| [docs/requisitos/](docs/requisitos/) | Requisitos numerados, com critérios Dado / Quando / Então |
| [docs/arquitetura/](docs/arquitetura/) | Processos, fluxos, orçamento, falhas |
| [docs/dados/](docs/dados/) | Esquema SQLite e JSON Schema |
| [docs/modelos/](docs/modelos/) | Fichas, prefixos, portas, lentes, confronto |
| [docs/interface/](docs/interface/) | Chrome, barra, leitor, copy |
| [docs/estrutura/](docs/estrutura/) | Árvore, módulos, contrato HTTP |
| [docs/planos/](docs/planos/) | PLN-01 … PLN-21 |
| [docs/rastreio/](docs/rastreio/) | Matriz origem → requisitos → planos |
| [docs/desenvolvimento/](docs/desenvolvimento/) | Arranque: ambiente, ondas, pacotes, convenções, regressão |
| [docs/verificacao/](docs/verificacao/) | Cobertura de cada requisito por uma regressão e como escolher um rascunho |

## Licença

O texto e o código futuros deste repositório: [Apache License 2.0](LICENSE). Os pesos dos modelos seguem as licenças das respectivas fichas Hugging Face; não estão neste repositório.
