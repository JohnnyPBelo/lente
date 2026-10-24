# Barra de escrita — `REQ-BAR`

## REQ-BAR-001

**Enunciado:** Tudo o que se escreve parte do mesmo sítio, no fundo do chat. Não há páginas novas para os gestos de modo.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** qualquer modo (Procurar, Correlacionar, Confrontar, Alerta, Lacunas), **quando** o utilizador escreve ou envia, **então** a interacção ocorre na barra no fundo do chat, sem navegar para uma rota/página dedicada a esse modo.

**Não pede:** barra flutuante destacável; atalhos globais fora da app.

---

## REQ-BAR-002

**Enunciado:** À esquerda do campo há um botão `+` que abre um menu curto, por cima da barra, em vidro.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** a barra visível, **quando** o utilizador activa o botão `+`, **então** abre-se um menu curto em vidro por cima da barra com os modos disponíveis.

**Não pede:** menu a ocupar ecrã inteiro; itens de exportar/importar correções neste menu (ver REQ-BAR-012).

---

## REQ-BAR-003

**Enunciado:** A tecla `/` abre o mesmo menu que o botão `+`.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** o foco na barra em condições em que `/` é o atalho de menu, **quando** o utilizador pressiona `/`, **então** abre-se o mesmo menu de modos que o `+`.

**Não pede:** `/` como carácter literal a ser impedido em todos os campos multi-linha sem Escape; comando slash estilo Discord além da lista de modos.

---

## REQ-BAR-004

**Enunciado:** No menu, as setas escolhem, Enter confirma, Escape volta a uma procura normal.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** o menu de modos aberto, **quando** o utilizador navega com setas e pressiona Enter, **então** o modo seleccionado fica activo.
2. **Dado** o menu aberto ou um modo especial activo conforme o fluxo, **quando** o utilizador pressiona Escape, **então** regressa ao modo Procurar (procura normal).

**Não pede:** atalhos numéricos; fechar a app com Escape.

---

## REQ-BAR-005

**Enunciado:** O modo activo fica uma pastilha na barra, para se ver o que se está a escrever.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** um modo diferente de Procurar activo, **quando** se olha para a barra, **então** há uma pastilha visível que identifica o modo activo.

**Não pede:** pastilha para cada lente e modo empilhadas sem limite visual; cor distinta por cada modo além do necessário para legibilidade.

---

## REQ-BAR-006

**Enunciado:** **Procurar** é o modo de repouso: uma linha; Enter envia.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** o modo Procurar, **quando** a barra está em repouso, **então** há um único campo de uma linha e Enter envia a procura.

**Não pede:** multi-linha no modo Procurar; envio automático sem Enter.

---

## REQ-BAR-007

**Enunciado:** **Correlacionar** parte a barra em dois campos, Conceito A e Conceito B; Enter envia os dois; o resultado é a mensagem de sempre, com as três cores e o leque.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** o modo Correlacionar, **quando** a barra se apresenta, **então** existem dois campos rotulados Conceito A e Conceito B.
2. **Dado** ambos preenchidos, **quando** o utilizador pressiona Enter, **então** ambos são enviados e a mensagem de resultado segue o fio habitual com três cores e leque (REQ-BUS-011).

**Não pede:** mais de dois conceitos; grafo visual separado do chat.

---

## REQ-BAR-008

**Enunciado:** **Confrontar** tem dois lugares, Trecho A e Trecho B, cada um com «escolher». Ao carregar, o chat escurece levemente e citações/trechos fixados ficam clicáveis; se não houver citações, aceita texto colado. Enviar pede ao juiz as três leituras: concordam, contradizem-se, ou assuntos diferentes. A resposta mostra as duas citações, a leitura e a pontuação. Clicar numa citação abre o leitor nesse highlight. Sem modelo novo: a leitura é função das duas direcções do juiz e do cosseno entre os trechos.

**Origem:** docs/origem/plano.md — «A barra de escrita»; fecho de lacuna (LEITURA — «Confronto determinístico»)

**Critérios de aceitação:**

1. **Dado** o modo Confrontar, **quando** a barra se apresenta, **então** há Trecho A e Trecho B com acção «escolher» em cada um.
2. **Dado** «escolher» activo, **quando** há citações ou trechos fixados na conversa, **então** o chat escurece levemente e esses alvos ficam clicáveis para encher o lugar com ficheiro e página.
3. **Dado** conversa sem citações, **quando** o lugar está vazio, **então** aceita texto colado.
4. **Dado** A e B preenchidos e enviados, **quando** o resultado aparece, **então** mostra as duas citações, uma das três leituras (concordam / contradizem-se / assuntos diferentes) e a pontuação; clicar numa citação abre o leitor no highlight.
5. **Dado** o confronto, **quando** se inspecciona o pipeline, **então** não há modelo adicional só para confronto — a leitura deriva das duas direcções do juiz e do cosseno.

**Não pede:** a lente a alterar as três leituras fixas do confronto; prosa livre do E2B no confronto.

---

## REQ-BAR-009

**Enunciado:** **Alerta** deixa a barra num campo só, com o placeholder «O que queres que eu vigie?». Enviar cria o alerta (até dez no total). Detalhe do comportamento de vigilância em REQ-ALE-*.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** o modo Alerta, **quando** a barra se apresenta, **então** há um único campo com o placeholder «O que queres que eu vigie?».
2. **Dado** menos de dez alertas, **quando** o utilizador envia texto nesse campo, **então** é criado um alerta.
3. **Dado** já dez alertas, **quando** o utilizador tenta criar outro, **então** a criação é recusada ou impedida de forma observável.

**Não pede:** alertas a rever a biblioteca antiga sozinhos (REQ-ALE-006); E2B no alerta.

---

## REQ-BAR-010

**Enunciado:** **Lacunas** cresce a barra para uma caixa de várias linhas (uma linha por controlo, hipótese ou pergunta). Shift+Enter parte a linha; Enter envia. Sai uma única mensagem: lista com encontrado, fraco ou ausente. A citação de cada linha abre o leitor. Vinte ou trinta linhas de uma vez, sem o E2B, e não se repete sozinha.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** o modo Lacunas, **quando** a barra se apresenta, **então** é uma caixa multi-linha; Shift+Enter insere nova linha e Enter envia.
2. **Dado** uma lista de linhas enviada (até ~20–30), **quando** o resultado aparece, **então** é uma única mensagem com estado encontrado / fraco / ausente por linha, e a citação de uma linha com prova abre o leitor.
3. **Dado** o modo Lacunas, **quando** corre o pipeline, **então** não chama o E2B e não volta a executar a lista sozinho em fundo.

**Não pede:** relatório exportável automático; reexecução periódica das lacunas.

---

## REQ-BAR-011

**Enunciado:** A lente de trabalho (investigar, assessment, acreditação, verificar) é outra pastilha na mesma barra, ao lado do modo. Muda a instrução da procura, do alerta e das lacunas. Não muda o confronto.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** a barra, **quando** o utilizador escolhe uma lente, **então** a pastilha da lente fica visível ao lado da pastilha do modo.
2. **Dado** lente alterada, **quando** corre Procurar, Alerta ou Lacunas, **então** a instrução/prefixos reflectem a lente (REQ-BUS-002 / REQ-RES-011).
3. **Dado** o modo Confrontar, **quando** a lente muda, **então** as três leituras do confronto permanecem as mesmas (concordam / contradizem-se / assuntos diferentes).

**Não pede:** lentes personalizadas pelo utilizador; lente a alterar o EmbeddingGemma base.

---

## REQ-BAR-012

**Enunciado:** Exportar e importar afinações **não** entra neste menu. Não há texto para escrever. Fica no estado da aprendizagem, no topo da barra lateral: «Exportar correções», «Importar correções».

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** o menu `+` / `/`, **quando** se listam as entradas, **então** não existem itens Exportar correções nem Importar correções.
2. **Dado** o topo da barra lateral (estado da aprendizagem), **quando** o utilizador procura essas acções, **então** encontra «Exportar correções» e «Importar correções» aí.

**Não pede:** atalho na barra de escrita para exportar; exportar o binário LoRA neste sítio (ver REQ-FBK-015).
