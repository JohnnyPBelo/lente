# Matriz plano → requisitos → planos

Fonte: [docs/origem/plano.md](../origem/plano.md). Cada linha cobre uma secção (título `##` ou a introdução sem título de nível 2). Destinos: `REQ-*` ([docs/requisitos/](../requisitos/)), `ADR-*` ([docs/decisoes/](../decisoes/)), `PLN-*` ([docs/planos/](../planos/)), e caminhos em `arquitetura/`, `dados/`, `modelos/`, `interface/`, `estrutura/`.

IDs `PLN-01` … `PLN-21` seguem a ordem acordada (esquema → ingestão → pesquisa → juiz → resposta → UI → feedback → dossier → alertas → diário/backup → estados/a11y/arranque).

## Tabela principal

| Secção de `plano.md` | REQ-* | ADR-* | PLN-* | Docs relacionados |
| --- | --- | --- | --- | --- |
| **Introdução** (app de secretária, 16 GB, GPU acelera o mesmo código, sem segundo modo) | `REQ-MOD-002`, `REQ-MOD-005`, `REQ-DES-003` | `ADR-006`, `ADR-007`, `ADR-008`, `ADR-013` | `PLN-10`, `PLN-12`, `PLN-13`, `PLN-21` | [arquitetura/visao.md](../arquitetura/visao.md), [arquitetura/orcamento.md](../arquitetura/orcamento.md), [arquitetura/processos.md](../arquitetura/processos.md), [estrutura/arvore.md](../estrutura/arvore.md), [interface/principios.md](../interface/principios.md) |
| **Que modelo faz de System One** | `REQ-JUI-001`, `REQ-JUI-002`, `REQ-JUI-004`, `REQ-FOR-005` | `ADR-003`, `ADR-005`, `ADR-007`, `ADR-016` | `PLN-08`, `PLN-16` | [modelos/juiz.md](../modelos/juiz.md), [modelos/licencas.md](../modelos/licencas.md), [arquitetura/visao.md](../arquitetura/visao.md) |
| **Três papéis, dois residentes** | `REQ-BUS-001`, `REQ-JUI-002`, `REQ-JUI-003`, `REQ-JUI-005`, `REQ-RES-002`, `REQ-RES-009`, `REQ-RES-010`, `REQ-MOD-009`, `REQ-FOR-004`, `REQ-FOR-007`, `REQ-FOR-009` | `ADR-001`, `ADR-003`, `ADR-004`, `ADR-007`, `ADR-012` | `PLN-06`, `PLN-08`, `PLN-11` | [modelos/embeddinggemma.md](../modelos/embeddinggemma.md), [modelos/juiz.md](../modelos/juiz.md), [modelos/e2b.md](../modelos/e2b.md), [arquitetura/visao.md](../arquitetura/visao.md), [arquitetura/orcamento.md](../arquitetura/orcamento.md), [estrutura/arvore.md](../estrutura/arvore.md) (`engine/pesquisa/`, `engine/juiz/`, `engine/escritor/`) |
| **Orçamento da máquina** | `REQ-ING-009`, `REQ-ING-011`, `REQ-BUS-012`, `REQ-FBK-009`, `REQ-FBK-018`, `REQ-MOD-003`, `REQ-MOD-004`, `REQ-MOD-005`, `REQ-MOD-006`, `REQ-MOD-009`, `REQ-DES-003` | `ADR-001`, `ADR-006`, `ADR-007` | `PLN-06`, `PLN-10`, `PLN-11`, `PLN-16` | [arquitetura/escalonador.md](../arquitetura/escalonador.md), [arquitetura/orcamento.md](../arquitetura/orcamento.md), [arquitetura/processos.md](../arquitetura/processos.md), [estrutura/arvore.md](../estrutura/arvore.md) (`engine/escalonador/`) |
| **Base vectorial** | `REQ-BUS-003`, `REQ-BUS-004`, `REQ-BUS-005`, `REQ-BUS-006`, `REQ-DES-001`, `REQ-FOR-001` | `ADR-002`, `ADR-015`, `ADR-016` | `PLN-01`, `PLN-07` | [dados/README.md](../dados/README.md), [dados/esquema.md](../dados/esquema.md), [arquitetura/visao.md](../arquitetura/visao.md), [estrutura/arvore.md](../estrutura/arvore.md) (`engine/armazenamento/`, `engine/indice/`) |
| **Dossier de prova** | `REQ-DOS-001` … `REQ-DOS-008`, `REQ-RES-009` | `ADR-011` (citações fiéis antes do fecho) | `PLN-18`, `PLN-01` | [dados/dossier.schema.json](../dados/dossier.schema.json), [dados/esquema.md](../dados/esquema.md), [arquitetura/fluxos.md](../arquitetura/fluxos.md), [interface/chat-e-leque.md](../interface/chat-e-leque.md), [estrutura/arvore.md](../estrutura/arvore.md) (`engine/armazenamento/`) |
| **A barra de escrita** — shell (`+`, `/`, pastilha, Escape) | `REQ-BAR-001` … `REQ-BAR-005`, `REQ-A11-002` | — | `PLN-14`, `PLN-13` | [interface/barra.md](../interface/barra.md), [interface/copy.md](../interface/copy.md) |
| **A barra de escrita** — Procurar | `REQ-BAR-003`, `REQ-BAR-005`, `REQ-BUS-002` | `ADR-009` | `PLN-09`, `PLN-12`, `PLN-14` | [interface/barra.md](../interface/barra.md), [modelos/prefixos-e-lentes.md](../modelos/prefixos-e-lentes.md), [arquitetura/fluxos.md](../arquitetura/fluxos.md) |
| **A barra de escrita** — Correlacionar | `REQ-BAR-006`, `REQ-BAR-007`, `REQ-BUS-011` | — | `PLN-09`, `PLN-14`, `PLN-15` | [interface/barra.md](../interface/barra.md), [arquitetura/fluxos.md](../arquitetura/fluxos.md), [modelos/fusao-limiar-platt.md](../modelos/fusao-limiar-platt.md) |
| **A barra de escrita** — Confrontar | `REQ-BAR-008`, `REQ-LEI-010` | `ADR-010` | `PLN-08`, `PLN-14`, `PLN-15` | [interface/barra.md](../interface/barra.md), [interface/leitor.md](../interface/leitor.md), [modelos/confronto.md](../modelos/confronto.md), [arquitetura/fluxos.md](../arquitetura/fluxos.md) |
| **A barra de escrita** — Alerta | `REQ-BAR-009`, `REQ-ALE-001` … `REQ-ALE-007`, `REQ-FOR-002` | `ADR-009` (alerta sem E2B) | `PLN-19`, `PLN-14` | [interface/barra.md](../interface/barra.md), [interface/barra-lateral.md](../interface/barra-lateral.md), [arquitetura/fluxos.md](../arquitetura/fluxos.md) |
| **A barra de escrita** — Lacunas | `REQ-BAR-010`, `REQ-RES-011` | `ADR-009` (lacunas sem E2B) | `PLN-09`, `PLN-14` | [interface/barra.md](../interface/barra.md), [arquitetura/fluxos.md](../arquitetura/fluxos.md) |
| **A barra de escrita** — Lentes | `REQ-BAR-011`, `REQ-BUS-002`, `REQ-RES-011` | `ADR-009` | `PLN-06`, `PLN-11`, `PLN-14` | [modelos/prefixos-e-lentes.md](../modelos/prefixos-e-lentes.md), [interface/barra.md](../interface/barra.md) |
| **A barra de escrita** — Exportar/importar fora do menu `+` | `REQ-BAR-012`, `REQ-FBK-017` | `ADR-005` | `PLN-17`, `PLN-13` | [interface/barra-lateral.md](../interface/barra-lateral.md), [dados/correcoes.schema.json](../dados/correcoes.schema.json) |
| **Mais, ainda sem peso** — SHA-256 / desactualizado | `REQ-ING-008` | — | `PLN-01`, `PLN-02` … `PLN-05`, `PLN-20` | [dados/esquema.md](../dados/esquema.md), [estrutura/arvore.md](../estrutura/arvore.md) (`engine/indice/`) |
| **Mais, ainda sem peso** — Diário local | `REQ-DIA-001`, `REQ-DIA-002`, `REQ-SEG-003`, `REQ-SEG-005` | `ADR-008` | `PLN-20` | [dados/esquema.md](../dados/esquema.md), [estrutura/arvore.md](../estrutura/arvore.md) (`engine/armazenamento/`) |
| **Mais, ainda sem peso** — Etiquetas | `REQ-BIB-001`, `REQ-BIB-002` | — | `PLN-20` | [dados/esquema.md](../dados/esquema.md), [interface/barra-lateral.md](../interface/barra-lateral.md) |
| **Mais, ainda sem peso** — Cópia de segurança | `REQ-BAK-001`, `REQ-BAK-002`, `REQ-SEG-005` | `ADR-008` | `PLN-20` | [dados/README.md](../dados/README.md), [estrutura/arvore.md](../estrutura/arvore.md) (`data/`) |
| **O chat e o leitor** — barra lateral e fio | `REQ-CHT-001`, `REQ-CHT-002`, `REQ-CHT-008` | `ADR-013` | `PLN-12`, `PLN-13`, `PLN-15` | [interface/barra-lateral.md](../interface/barra-lateral.md), [interface/chat-e-leque.md](../interface/chat-e-leque.md), [interface/movimento.md](../interface/movimento.md) |
| **O chat e o leitor** — leque e miniaturas | `REQ-CHT-003` … `REQ-CHT-007`, `REQ-ING-011`, `REQ-A11-001` | — | `PLN-15`, `PLN-21` | [interface/chat-e-leque.md](../interface/chat-e-leque.md), [interface/movimento.md](../interface/movimento.md), [arquitetura/fluxos.md](../arquitetura/fluxos.md) |
| **O chat e o leitor** — leitor (PDF/texto/MD/URL/imagem) | `REQ-LEI-001` … `REQ-LEI-011`, `REQ-ING-010`, `REQ-RES-009` | `ADR-012` | `PLN-03`, `PLN-15` | [interface/leitor.md](../interface/leitor.md), [interface/principios.md](../interface/principios.md), [estrutura/arvore.md](../estrutura/arvore.md) (`apps/ui/`) |
| **A resposta, sem reaproveitar respostas velhas** | `REQ-BUS-008`, `REQ-RES-001` … `REQ-RES-008`, `REQ-RES-010`, `REQ-FOR-006`, `REQ-FOR-007` | `ADR-004`, `ADR-011` | `PLN-11`, `PLN-12` | [modelos/e2b.md](../modelos/e2b.md), [modelos/duas-portas.md](../modelos/duas-portas.md), [arquitetura/fluxos.md](../arquitetura/fluxos.md), [estrutura/arvore.md](../estrutura/arvore.md) (`engine/escritor/`) |
| **Feedback, só no juiz** | `REQ-FBK-001` … `REQ-FBK-010`, `REQ-JUI-004`, `REQ-JUI-005`, `REQ-LEI-007` | `ADR-005`, `ADR-006` | `PLN-16`, `PLN-08` | [arquitetura/fluxos.md](../arquitetura/fluxos.md), [modelos/juiz.md](../modelos/juiz.md), [interface/chat-e-leque.md](../interface/chat-e-leque.md), [dados/esquema.md](../dados/esquema.md) |
| **Juntar afinações** (incl. diagrama mermaid do fluxo) | `REQ-FBK-011` … `REQ-FBK-018`, `REQ-SEG-004`, `REQ-FOR-003` | `ADR-005`, `ADR-016` | `PLN-16`, `PLN-17` | [dados/correcoes.schema.json](../dados/correcoes.schema.json), [interface/barra-lateral.md](../interface/barra-lateral.md), [arquitetura/fluxos.md](../arquitetura/fluxos.md), [arquitetura/escalonador.md](../arquitetura/escalonador.md) |
| **Pesquisa, sem modelo a mais** | `REQ-BUS-002`, `REQ-BUS-003`, `REQ-BUS-007`, `REQ-BUS-009`, `REQ-BUS-010`, `REQ-BUS-011`, `REQ-BIB-002`, `REQ-BIB-003`, `REQ-DES-002` | `ADR-009`, `ADR-010`, `ADR-014`, `ADR-015` | `PLN-07`, `PLN-09`, `PLN-06` | [modelos/prefixos-e-lentes.md](../modelos/prefixos-e-lentes.md), [modelos/fusao-limiar-platt.md](../modelos/fusao-limiar-platt.md), [dados/esquema.md](../dados/esquema.md), [estrutura/arvore.md](../estrutura/arvore.md) (`engine/pesquisa/`) |
| **Entradas** | `REQ-ING-001` … `REQ-ING-011`, `REQ-SEG-001` | `ADR-012`, `ADR-008` | `PLN-02`, `PLN-03`, `PLN-04`, `PLN-05`, `PLN-06`, `PLN-01` | [dados/esquema.md](../dados/esquema.md), [estrutura/arvore.md](../estrutura/arvore.md) (`engine/ingestao/`, `engine/indice/`), [arquitetura/falhas.md](../arquitetura/falhas.md) |
| **Interface** | `REQ-CHT-001`, `REQ-CHT-008`, `REQ-LEI-009`, `REQ-DOS-008`, `REQ-VAZ-001`, `REQ-A11-001`, `REQ-A11-002` | `ADR-013` | `PLN-13`, `PLN-15`, `PLN-18`, `PLN-21` | [interface/principios.md](../interface/principios.md), [interface/estados-vazios.md](../interface/estados-vazios.md), [interface/movimento.md](../interface/movimento.md), [interface/copy.md](../interface/copy.md) |
| **Como corre** | `REQ-MOD-001`, `REQ-MOD-002`, `REQ-MOD-007`, `REQ-MOD-008`, `REQ-RES-008`, `REQ-SEG-002` | `ADR-013`, `ADR-008` | `PLN-12`, `PLN-21`, `PLN-10` | [arquitetura/processos.md](../arquitetura/processos.md), [arquitetura/falhas.md](../arquitetura/falhas.md), [estrutura/README.md](../estrutura/README.md), [estrutura/arvore.md](../estrutura/arvore.md), [estrutura/contrato-http.md](../estrutura/contrato-http.md) |
| **De fora, porque pesa ou muda o modelo** | `REQ-FOR-001` … `REQ-FOR-010`, `REQ-ALE-006`, `REQ-SEG-003`, `REQ-SEG-006` | `ADR-016` (e exclusões em `ADR-002`, `ADR-003`, `ADR-004`, `ADR-005`, `ADR-008`) | — (nenhum plano implementa o excluído; a verificação vive nos REQ-FOR e nos testes dos PLN que tocam o mesmo perímetro) | [decisoes/ADR-016-fora-de-ambito.md](../decisoes/ADR-016-fora-de-ambito.md), [requisitos/fora-de-ambito.md](../requisitos/fora-de-ambito.md), [arquitetura/visao.md](../arquitetura/visao.md) |

### Cobertura de títulos `##` de `plano.md`

| Título exacto em `plano.md` | Linha(s) na tabela |
| --- | --- |
| *(introdução sem `##`)* | Introdução |
| Que modelo faz de System One | Que modelo faz de System One |
| Três papéis, dois residentes | Três papéis, dois residentes |
| Orçamento da máquina | Orçamento da máquina |
| Base vectorial | Base vectorial |
| Dossier de prova | Dossier de prova |
| A barra de escrita | A barra de escrita (shell + Procurar + Correlacionar + Confrontar + Alerta + Lacunas + Lentes + Exportar/importar) |
| Mais, ainda sem peso | Mais, ainda sem peso (SHA-256 + Diário + Etiquetas + Cópia) |
| O chat e o leitor | O chat e o leitor (barra lateral/fio + leque + leitor) |
| A resposta, sem reaproveitar respostas velhas | A resposta… |
| Feedback, só no juiz | Feedback, só no juiz |
| Juntar afinações | Juntar afinações |
| Pesquisa, sem modelo a mais | Pesquisa, sem modelo a mais |
| Entradas | Entradas |
| Interface | Interface |
| Como corre | Como corre |
| De fora, porque pesa ou muda o modelo | De fora… |

## Índice inverso: REQ → plano

| Área `REQ` | Prefixo | Secções de `plano.md` |
| --- | --- | --- |
| Ingestão e indexação | `REQ-ING` | Entradas; Mais, ainda sem peso (SHA-256); Orçamento da máquina (fila / miniaturas); O chat e o leitor (sumário) |
| Pesquisa | `REQ-BUS` | Três papéis…; Base vectorial; Pesquisa, sem modelo a mais; A barra de escrita (Procurar / Correlacionar / Lentes); A resposta…; Orçamento da máquina |
| Juiz / highlight | `REQ-JUI` | Que modelo faz de System One; Três papéis…; Feedback, só no juiz |
| Resposta e portas | `REQ-RES` | A resposta…; Três papéis…; O chat e o leitor; Como corre; A barra de escrita (Lacunas / Lentes) |
| Chat e leque | `REQ-CHT` | O chat e o leitor; Interface |
| Barra de escrita | `REQ-BAR` | A barra de escrita (todos os modos); Feedback / afinações (exportação fora do menu) |
| Leitor | `REQ-LEI` | O chat e o leitor; A barra de escrita (Confrontar); Feedback, só no juiz; Interface |
| Dossier | `REQ-DOS` | Dossier de prova; Interface |
| Feedback / LoRA / afinações | `REQ-FBK` | Feedback, só no juiz; Juntar afinações; Orçamento da máquina; A barra de escrita (estado de aprendizagem) |
| Biblioteca | `REQ-BIB` | Mais, ainda sem peso (etiquetas); Pesquisa, sem modelo a mais |
| Alertas | `REQ-ALE` | A barra de escrita (Alerta); De fora… |
| Diário | `REQ-DIA` | Mais, ainda sem peso |
| Cópia de segurança | `REQ-BAK` | Mais, ainda sem peso |
| Runtime e modelos | `REQ-MOD` | Introdução; Orçamento da máquina; Como corre; Três papéis… |
| Estados vazios | `REQ-VAZ` | Interface; Entradas (URL recusada) |
| Acessibilidade | `REQ-A11` | O chat e o leitor; A barra de escrita |
| Segurança | `REQ-SEG` | Entradas; Como corre; Mais, ainda sem peso; Juntar afinações; De fora… |
| Desempenho | `REQ-DES` | Base vectorial; Pesquisa…; Orçamento da máquina; Introdução |
| Fora de âmbito | `REQ-FOR` | De fora…; Base vectorial; Que modelo faz de System One; Três papéis…; A resposta…; Juntar afinações; A barra de escrita (alerta) |

## Referência rápida PLN-01 … PLN-21

| ID | Título (ordem acordada) |
| --- | --- |
| `PLN-01` | Esquema SQLite e migrações |
| `PLN-02` | Texto, Markdown e docx |
| `PLN-03` | PDF com texto e caixas |
| `PLN-04` | OCR (Tesseract) |
| `PLN-05` | URL e recusa de endereços privados |
| `PLN-06` | Blocos, frases e embeddings (EmbeddingGemma 256d) |
| `PLN-07` | FTS5 e cosseno exacto (sqlite-vec) |
| `PLN-08` | Juiz ONNX |
| `PLN-09` | Fusão RRF, limiar e Platt |
| `PLN-10` | Escalonador (um trabalho pesado) |
| `PLN-11` | Escritor E2B e duas portas |
| `PLN-12` | API do chat (HTTP) |
| `PLN-13` | Chrome da interface |
| `PLN-14` | Barra de modos e lentes |
| `PLN-15` | Leque e leitor |
| `PLN-16` | Feedback e LoRA do juiz |
| `PLN-17` | Importar e exportar correcções |
| `PLN-18` | Dossier |
| `PLN-19` | Alertas |
| `PLN-20` | Diário, etiquetas e cópia de segurança |
| `PLN-21` | Estados vazios, acessibilidade e comando único |

## Buracos

Nenhum. Todas as secções `##` de [docs/origem/plano.md](../origem/plano.md) e a introdução sem `##` têm destino na tabela principal (REQ e/ou ADR e/ou PLN e docs relacionados). A secção «De fora…» mapeia para `REQ-FOR-*` e `ADR-016` (exclusões), sem plano de implementação do comportamento excluído.
