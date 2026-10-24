# Modelo de dados — Lente

Documentação do esquema SQLite e dos formatos JSON de exportação, derivados de [docs/origem/plano.md](../origem/plano.md).

Tudo vive num único ficheiro SQLite em `data/`, com a extensão [`sqlite-vec`](https://github.com/asg017/sqlite-vec) no mesmo processo. Não há base vectorial à parte: documentos, FTS5, chats, feedback, dossiers e vectores de 256 dimensões partilham o mesmo ficheiro. Uma cópia leva o índice consigo.

## Conteúdo desta pasta

| Ficheiro | Conteúdo |
| --- | --- |
| [esquema.md](esquema.md) | Tabelas, chaves, índices e notas de integração `sqlite-vec` / FTS5 |
| [dossier.schema.json](dossier.schema.json) | JSON Schema do export JSON do dossier de prova |
| [correcoes.schema.json](correcoes.schema.json) | JSON Schema do ficheiro de exportação/importação de correções do juiz |
| [exemplos/](exemplos/) | Exemplos sintéticos (frases inventadas, não documentos reais) |

## Princípios

- **Um ficheiro, um processo.** Vectores com cosseno exacto via `sqlite-vec`; FTS5 para termo exacto; fusão por rank recíproco no código.
- **Prova congelada.** Fechar um dossier grava fotografia (perguntas, frases, offsets, caixas, pontuação do juiz, SHA-256 dos bytes, versões de modelo). Reabrir não volta a correr modelos.
- **Afinações partilháveis.** Exportar correções entrega JSON (pergunta, trecho, etiqueta, lente, hash do par), não o binário LoRA.
- **Diário só de acrescentar.** Procuras, aberturas, feedback e fechos; sem contas nem rede.

## Idioma

Português de Portugal em nomes de tabelas/colunas documentados, descrições e exemplos.
