# Especificação de interface — Lente

Especificação visual e de interacção da UI, em português de Portugal, derivada de [docs/origem/plano.md](../origem/plano.md). Complementa requisitos (`REQ-CHT`, `REQ-BAR`, `REQ-LEI`, `REQ-VAZ`, `REQ-A11`, `REQ-FBK`, `REQ-ALE`) sem os substituir: aqui ficam layout, chrome, gestos, movimento e copy exacta.

App de secretária no browser (`127.0.0.1:4317`). Sem Electron. Sem i18n multi-língua: a interface fala português.

## Conteúdo desta pasta

| Ficheiro | Conteúdo |
| --- | --- |
| [principios.md](principios.md) | Vidro líquido, tipografia, shadcn/motion, idioma |
| [barra.md](barra.md) | Barra de escrita, menu `+`/`/`, modos, pastilhas, Escape |
| [chat-e-leque.md](chat-e-leque.md) | Fio, prosa+citações, leque um/vários, tacto, reduced motion |
| [leitor.md](leitor.md) | Documento inteiro, scroll, highlights, zoom, TOC, Confrontar, fixar |
| [barra-lateral.md](barra-lateral.md) | Conversas CRUD, grupo Alertas, estado de aprendizagem |
| [estados-vazios.md](estados-vazios.md) | Os sete estados vazios do plano |
| [movimento.md](movimento.md) | Animações curtas obrigatórias |
| [copy.md](copy.md) | Strings de UI em português de Portugal (inclui introdução no primeiro uso) |

## Ordem de leitura sugerida

1. [principios.md](principios.md)
2. [barra.md](barra.md) e [barra-lateral.md](barra-lateral.md)
3. [chat-e-leque.md](chat-e-leque.md) → [leitor.md](leitor.md)
4. [estados-vazios.md](estados-vazios.md), [movimento.md](movimento.md), [copy.md](copy.md)

## Fonte de verdade

Não reescrever o plano. Em conflito de intenção, [docs/origem/plano.md](../origem/plano.md) e as decisões em [docs/LEITURA.md](../LEITURA.md) ganham; este pacote só detalha a superfície.
