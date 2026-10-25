# Planos de implementação (PLN-01 … PLN-21)

Guias para construir a Lente. Cada plano nomeia ficheiros futuros e o primeiro teste que deve falhar. Estes ficheiros ainda não existem no repositório: o código entra quando o plano for executado.

Fonte de verdade: [docs/origem/plano.md](../origem/plano.md). Como ler IDs e aceitação: [docs/LEITURA.md](../LEITURA.md).

## Como usar

1. Seguir a ordem abaixo: cada plano assume os anteriores concluídos (ou stubs mínimos acordados).
2. Implementar tarefa a tarefa; passos usam `- [ ]`.
3. Estilo TDD: escrever o teste que falha → implementar o mínimo → fazer passar → commit.
4. Commits frequentes, mensagens em português (Portugal).
5. Um plano está feito quando todas as caixas estão marcadas e o teste nomeado (e os seguintes do plano) passam.

## Ordem

| Plano | Título | Pasta futura principal |
| --- | --- | --- |
| [PLN-01](PLN-01-esquema-sqlite-e-migracoes.md) | Esquema SQLite e migrações | `engine/armazenamento/` |
| [PLN-02](PLN-02-texto-markdown-e-docx.md) | Texto, Markdown e docx | `engine/ingestao/` |
| [PLN-03](PLN-03-pdf-com-texto-e-caixas.md) | PDF com texto e caixas | `engine/ingestao/` |
| [PLN-04](PLN-04-ocr-tesseract.md) | OCR (Tesseract) | `engine/ingestao/` |
| [PLN-05](PLN-05-url-e-recusa-privados.md) | URL e recusa de endereços privados | `engine/ingestao/` |
| [PLN-06](PLN-06-blocos-frases-e-embeddings.md) | Blocos, frases e embeddings (EmbeddingGemma 256d) | `engine/embeddings/` |
| [PLN-07](PLN-07-fts5-e-cosseno-exacto.md) | FTS5 e cosseno exacto (sqlite-vec) | `engine/pesquisa/` |
| [PLN-08](PLN-08-juiz-onnx.md) | Juiz ONNX | `engine/juiz/` |
| [PLN-09](PLN-09-fusao-rrf-limiar-e-platt.md) | Fusão RRF, limiar e Platt | `engine/pesquisa/` |
| [PLN-10](PLN-10-escalonador.md) | Escalonador (um trabalho pesado) | `engine/escalonador/` |
| [PLN-11](PLN-11-escritor-e2b-e-duas-portas.md) | Escritor E2B e duas portas | `engine/resposta/` |
| [PLN-12](PLN-12-api-do-chat-http.md) | API do chat (HTTP) | `engine/api/` |
| [PLN-13](PLN-13-chrome-da-interface.md) | Chrome da interface | `apps/ui/` |
| [PLN-14](PLN-14-barra-de-modos-e-lentes.md) | Barra de modos e lentes | `apps/ui/` |
| [PLN-15](PLN-15-leque-e-leitor.md) | Leque e leitor | `apps/ui/` |
| [PLN-16](PLN-16-feedback-e-lora-do-juiz.md) | Feedback e LoRA do juiz | `engine/feedback/` |
| [PLN-17](PLN-17-importar-e-exportar-correcoes.md) | Importar e exportar correcções | `engine/feedback/` |
| [PLN-18](PLN-18-dossier.md) | Dossier | `engine/dossier/` |
| [PLN-19](PLN-19-alertas.md) | Alertas | `engine/alertas/` |
| [PLN-20](PLN-20-diario-etiquetas-e-copia-de-seguranca.md) | Diário, etiquetas e cópia de segurança | `engine/` |
| [PLN-21](PLN-21-estados-vazios-a11y-e-comando-unico.md) | Estados vazios, acessibilidade e comando único | `apps/ui/`, raiz |

## Fora destes planos

Base vectorial separada, índice aproximado, encoder de visão, Jev/clones locais de System One, fine-tune do E2B, contas/sincronização, áudio, e qualquer geração de procedimentos de ataque — ver plano de origem, secção «De fora».
