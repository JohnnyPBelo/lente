# Estados vazios — `REQ-VAZ`

## REQ-VAZ-001

**Enunciado:** A interface cobre explicitamente os estados vazios do plano: biblioteca sem ficheiros; modelo a descarregar; prosa toda filtrada; página sem texto; URL recusada; conversa nova; procura sem documentos.

**Origem:** docs/origem/plano.md — «Interface» (Estados vazios)

**Critérios de aceitação:**

1. **Dado** a biblioteca sem ficheiros, **quando** o utilizador a abre, **então** vê um estado vazio dedicado (não uma lista em branco sem explicação).
2. **Dado** um modelo a descarregar, **quando** a UI está aberta, **então** há indicação observável de download em curso.
3. **Dado** uma resposta em que toda a prosa foi filtrada pelas portas mas há trechos/miniaturas ou só aviso, **quando** a mensagem termina, **então** o estado correspondente é claro (excertos/miniaturas ou vazio — REQ-RES-007), sem prosa fantasma.
4. **Dado** uma página/documento sem texto extraível útil, **quando** o utilizador a abre ou indexa, **então** há estado/aviso de página sem texto.
5. **Dado** uma URL privada ou recusada, **quando** a ingestão falha, **então** o estado «URL recusada» é mostrado (REQ-ING-007).
6. **Dado** uma conversa nova sem mensagens, **quando** o utilizador a abre, **então** há estado de conversa nova (pronta a primeira procura), não um erro.
7. **Dado** uma procura sem documentos acima do limiar, **quando** a mensagem termina, **então** aparece o aviso de que não há nada acima do limiar e não há documentos/miniaturas a fingir hits.

**Não pede:** ilustrações obrigatórias em cada estado; i18n além do português da app.
