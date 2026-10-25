# Leitor

Origem: `docs/origem/plano.md` — «O chat e o leitor»; «A barra de escrita» (bolha Confrontar). Requisitos: `REQ-LEI-*`.

Abre o **documento inteiro** (não só o excerto): PDF, texto, Markdown, página de URL ou imagem.

## Superfície

- **Corpo**: superfície sólida + tipografia **serif**.
- **Chrome** do leitor (toolbar, páginas, sumário, bolhas): vidro + **Geist**.
- Ver [principios.md](principios.md).

## Navegação e vista

| Capacidade | Comportamento |
| --- | --- |
| Scroll | **Contínuo** ao longo do documento |
| Highlights | Visíveis em **todas** as páginas atingidas; salto entre marcas |
| Zoom | Controlo de escala |
| Arrastar | Pan em imagem ou scan quando o zoom o pede |
| Ajustar | À **largura** e à **página** |
| Páginas | Indicador; **ir para** uma página |
| Procurar neste documento | Pesquisa de texto **dentro** do documento aberto (não EmbeddingGemma) |
| Sumário (TOC) | Títulos **extraídos na indexação**; navegar para a secção |

## Highlights

- Cada marca é um **intervalo literal** do ficheiro (offsets / caixas da ingestão).
- Ao abrir a partir de uma citação: o highlight **acende uma vez** ([movimento.md](movimento.md)).
- Não pisca em ciclo.

## Selecção e citação

Com texto seleccionado (ou a partir de um highlight):

- **Copiar** — texto na área de transferência.
- **Copiar citação** — inclui **ficheiro** e **página**.
- A selecção serve o fluxo **Corrigir** do feedback (marcas da resposta → negativas; selecção → positiva).
- **Fixar trecho** — grava uma linha no SQLite ligada à mensagem; ao reabrir o chat o trecho está lá **sem** nova procura.

## Bolha Confrontar

Com texto seleccionado no leitor:

1. Aparece a bolha **Confrontar**.
2. Activa o modo Confrontar na barra.
3. Enche o **primeiro lugar vazio** (Trecho A ou B) com a selecção / ficheiro / página.
4. Devolve o foco à barra para escolher o segundo.

Não preenche os dois lugares com a mesma selecção.

## Fechar / minimizar

- **Minimizar** ou **Escape**: o leitor **recolhe** até à miniatura de origem; o chat permanece no mesmo sítio.
- Não fecha a conversa nem apaga a mensagem.

## O que o leitor não faz

- Edição in-place do ficheiro fonte.
- Anotações desenhadas livres.
- Sumário gerado por LLM se a extracção na indexação falhou.
- Formato académico configurável (APA/ISO) para a citação copiada.
