# Chat e leque

Origem: `docs/origem/plano.md` — «O chat e o leitor»; «A resposta, sem reaproveitar respostas velhas»; «Feedback, só no juiz». Requisitos: `REQ-CHT-*`, `REQ-RES-*`, `REQ-FBK-*`.

## Layout

- **Barra lateral** em vidro: conversas e Alertas ([barra-lateral.md](barra-lateral.md)).
- **Fio** ao centro: mensagens do utilizador e da app.
- **Barra de escrita** no fundo ([barra.md](barra.md)).

Não há segundo painel obrigatório para o leque: o leque nasce **na mensagem**, a partir das miniaturas.

## Resposta no fio

Ordem observável:

1. **Miniaturas** (quando há documentos acima do limiar) — podem aparecer primeiro.
2. **Prosa** só depois das duas portas: cada frase com `[n]` fiel ao trecho; caso contrário a frase não entra.
3. Se nenhuma frase sobreviver: ficam **excertos + miniaturas**, ou só o **aviso de vazio** ([estados-vazios.md](estados-vazios.md)). Sem prosa fantasma a ser apagada.

Cada frase que passou é um **link de citação**. Clicar abre o leitor nessa página, com o highlight à vista — **sem** passar pelo leque.

Correlacionar: mesma mensagem, com **três cores** (conceito A, conceito B, relação).

## Miniaturas

- Uma miniatura **por documento**, na página do **primeiro** highlight desse documento.
- Miniaturas são imagens pequenas geradas na indexação — não re-render do PDF no hover.

## Um documento vs. vários

| Quantidade | Rato / ponteiro | Tacto |
| --- | --- | --- |
| **Um** | Clique na miniatura → abre o leitor (crescimento até ao leitor) | Toque → abre o leitor |
| **Vários** | Hover / activação abre o **leque** ainda em miniatura; clique numa → essa cresce até ao leitor | **Primeiro toque** abre o leque; **segundo toque** numa miniatura abre o documento |

O leque não tira o fio: o chat mantém a posição. Minimizar ou **Escape** no leitor recolhe até à miniatura; o scroll do chat fica no mesmo sítio.

## Feedback na mensagem

Linha pequena sob a resposta com highlights:

- **Acertou**
- **Corrigir**
- **Descartar**

Não bloqueia a procura seguinte. Descartar não treina. Link discreto **Corrigir mais tarde** permanece na mensagem. Copy exacta em [copy.md](copy.md).

## `prefers-reduced-motion`

Com `prefers-reduced-motion: reduce`:

- Animações de mensagem, leque, crescimento e highlight **encurtam** ou saltam para o estado final quase de imediato.
- O **leque** e o **leitor** continuam presentes e utilizáveis — não se remove a funcionalidade.

Detalhe das animações nominais: [movimento.md](movimento.md).

## O que o chat não faz

- Não injeta respostas antigas no prompt do escritor.
- Não abre todos os documentos em separadores.
- Não exige passar pelo leque para seguir uma citação.
