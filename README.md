# Lente

Chat de pesquisa local com prova na página. Corre no browser em `127.0.0.1:4317`, no mesmo processo que o motor. Windows, macOS e Linux. Alvo: 16 GB de RAM, com ou sem GPU, o mesmo código.

Quem for implementar ou correr localmente começa por [docs/desenvolvimento/](docs/desenvolvimento/).

## Como correr

Piso: **Python 3.11+**, **Node 22** (só para construir a UI), **16 GB** de RAM, Tesseract.

```bash
# 1. Dependências do motor
python3 -m pip install -r requirements.txt

# 2. Construir a UI (Node 22; não fica a correr depois)
cd apps/ui && npm ci && npm run build && cd ../..

# 3. Um comando sobe UI + motor em 127.0.0.1:4317
./scripts/lente
# ou: python3 -m engine.cli
```

Abre `http://127.0.0.1:4317`. Sem argumentos o porto é **4317**; só escuta em **127.0.0.1**.

Os pesos ficam em `models/` (fora do git). Se o Hugging Face bloquear o download, a app **abre na mesma** e em `/models/guidance` (e no estado «A descarregar o modelo») indica onde pôr o ficheiro — por exemplo `models/embeddinggemma-2`, `models/juiz`, `models/e2b`. Sem o E2B o chat segue com excertos e miniaturas.

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
