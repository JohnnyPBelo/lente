# Barra de escrita

Origem: `docs/origem/plano.md` — «A barra de escrita». Requisitos: `REQ-BAR-*`.

Tudo o que se escreve parte do **mesmo sítio**, no fundo do chat. Não há rotas nem páginas dedicadas aos modos.

## Anatomia (da esquerda para a direita)

1. Botão **`+`**
2. Campo(s) do modo activo
3. Pastilha do **modo** (quando ≠ Procurar)
4. Pastilha da **lente** (sempre visível como pastilha de trabalho)
5. Envio implícito por **Enter** (salvo onde Shift+Enter parte linha)

O chrome da barra é vidro líquido ([principios.md](principios.md)).

## Menu `+` e `/`

- **`+`** abre um menu curto **por cima da barra**, em vidro.
- **`/`** (atalho na barra) abre o **mesmo** menu.
- **Setas** escolhem o item; **Enter** confirma; **Escape** fecha e volta a **Procurar** (procura normal).
- Itens do menu: **Procurar**, **Correlacionar**, **Confrontar**, **Alerta**, **Lacunas**.
- **Não** entram neste menu: Exportar correções, Importar correções (ficam na barra lateral — [barra-lateral.md](barra-lateral.md)).

## Pastilhas

| Pastilha | Quando | Função |
| --- | --- | --- |
| Modo activo | Modo ≠ Procurar | Mostra o que se está a escrever (Correlacionar, Confrontar, Alerta, Lacunas) |
| Lente | Sempre | Investigar / Assessment / Acreditação / Verificar |

A lente muda a instrução de **Procurar**, **Alerta** e **Lacunas**. **Não** muda o Confrontar (leituras fixas).

## Modos

### Procurar (repouso)

- Um campo, **uma linha**.
- **Enter** envia.
- Escape a partir de outro modo regressa aqui.

### Correlacionar

- A barra parte-se em **dois** campos: **Conceito A** e **Conceito B**.
- **Enter** envia os dois.
- Resultado: mensagem habitual com **três cores** (A, B, relação) e leque.

### Confrontar

- Dois lugares: **Trecho A** e **Trecho B**.
- Cada um tem acção **Escolher**.
- Ao activar Escolher: o chat **escurece levemente**; citações e trechos **fixados** desta conversa ficam clicáveis; o lugar enche-se com ficheiro e página.
- Sem citações: o lugar aceita **texto colado**.
- Enviar: juiz devolve uma das três leituras — **concordam**, **contradizem-se**, **falam de assuntos diferentes** — mais pontuação e as duas citações.
- Clicar numa citação abre o leitor nesse highlight.
- No leitor, bolha **Confrontar** com selecção → enche o primeiro lugar vazio e devolve o foco à barra ([leitor.md](leitor.md)).

### Alerta

- Um campo; placeholder: **O que queres que eu vigie?**
- Enviar cria o alerta (máximo **dez** no total).
- O fio do alerta e o interruptor vivem na barra lateral / topo do fio ([barra-lateral.md](barra-lateral.md)).

### Lacunas

- Caixa de **várias linhas**: uma linha por controlo, hipótese ou pergunta.
- **Shift+Enter** nova linha; **Enter** envia.
- Uma única mensagem: lista **encontrado** / **fraco** / **ausente**; citação abre o leitor.
- Até ~20–30 linhas; sem E2B; não se repete sozinha.

## Escape

| Contexto | Escape |
| --- | --- |
| Menu `+`/`/` aberto | Fecha menu → **Procurar** |
| Modo especial activo | Volta a **Procurar** |
| Leitor aberto | Recolhe leitor (ver chat/leitor); não redefine o modo sozinho salvo o fluxo Confrontar a pedir segundo trecho |

## O que a barra não faz

- Não aloja exportar/importar afinações.
- Não abre páginas novas por modo.
- Não altera as três leituras do confronto via lente.
