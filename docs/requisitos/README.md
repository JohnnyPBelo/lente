# Requisitos numerados — Lente

Requisitos derivados de [docs/origem/plano.md](../origem/plano.md) e das decisões de fecho em [docs/LEITURA.md](../LEITURA.md). Cada requisito tem ID, enunciado, origem, critérios de aceitação observáveis (Dado / Quando / Então) e o que **não** pede.

Um requisito está cumprido quando os seus critérios passam. Critérios usam gestos ou estados verificáveis; sem «rápido» ou «intuitivo» sem medida.

## Áreas

| Ficheiro | Prefixo | Área | IDs |
| --- | --- | --- | --- |
| [ingestao.md](ingestao.md) | `REQ-ING` | Ingestão e indexação | 001–011 |
| [pesquisa.md](pesquisa.md) | `REQ-BUS` | Pesquisa (embedding, FTS5, fusão) | 001–012 |
| [juiz.md](juiz.md) | `REQ-JUI` | Juiz / highlight | 001–005 |
| [resposta.md](resposta.md) | `REQ-RES` | Resposta e portas | 001–011 |
| [chat.md](chat.md) | `REQ-CHT` | Chat e leque | 001–008 |
| [barra.md](barra.md) | `REQ-BAR` | Barra de escrita e modos | 001–012 |
| [leitor.md](leitor.md) | `REQ-LEI` | Leitor de documento | 001–011 |
| [dossier.md](dossier.md) | `REQ-DOS` | Dossier de prova | 001–008 |
| [feedback.md](feedback.md) | `REQ-FBK` | Feedback, LoRA e afinações | 001–018 |
| [biblioteca.md](biblioteca.md) | `REQ-BIB` | Biblioteca | 001–003 |
| [alertas.md](alertas.md) | `REQ-ALE` | Alertas | 001–007 |
| [diario.md](diario.md) | `REQ-DIA` | Diário local | 001–002 |
| [backup.md](backup.md) | `REQ-BAK` | Cópia de segurança | 001–002 |
| [runtime.md](runtime.md) | `REQ-MOD` | Runtime e modelos | 001–009 |
| [estados-vazios.md](estados-vazios.md) | `REQ-VAZ` | Estados vazios | 001 |
| [acessibilidade.md](acessibilidade.md) | `REQ-A11` | Acessibilidade | 001–002 |
| [seguranca.md](seguranca.md) | `REQ-SEG` | Segurança e superfície local | 001–006 |
| [desempenho.md](desempenho.md) | `REQ-DES` | Desempenho e orçamento | 001–003 |
| [fora-de-ambito.md](fora-de-ambito.md) | `REQ-FOR` | Fora de âmbito (comportamento a manter) | 001–010 |

## Convenções

- **Origem** aponta a secção de `docs/origem/plano.md`, ou regista `fecho de lacuna` quando a regra vem das decisões em `docs/LEITURA.md` (não reescritas no plano).
- **Não pede** delimita o âmbito: o que a implementação não tem de fazer para cumprir este ID.
- Português de Portugal em toda a especificação de requisitos.
