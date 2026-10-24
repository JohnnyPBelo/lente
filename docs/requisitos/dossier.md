# Dossier de prova — `REQ-DOS`

## REQ-DOS-001

**Enunciado:** Cada frase da resposta que passou as duas portas é um link de prova.

**Origem:** docs/origem/plano.md — «Dossier de prova»

**Critérios de aceitação:**

1. **Dado** uma resposta com frases que passaram as duas portas, **quando** o utilizador vê o fio, **então** cada uma dessas frases é activável como link (não texto morto sem destino de prova).

**Não pede:** links em frases filtradas pelas portas; links para documentos fora do pacote da procura.

---

## REQ-DOS-002

**Enunciado:** Clicar numa frase-link abre o leitor nessa página, com o highlight já à vista. Não é preciso passar pelo leque para seguir uma citação; o leque continua lá para escolher um documento à mão.

**Origem:** docs/origem/plano.md — «Dossier de prova»

**Critérios de aceitação:**

1. **Dado** uma frase citada no fio, **quando** o utilizador clica nela, **então** o leitor abre na página e highlight correspondentes sem exigir abrir o leque primeiro.
2. **Dado** vários documentos na mensagem, **quando** o utilizador prefere escolher à mão, **então** o leque continua disponível.

**Não pede:** abrir o dossier automaticamente ao clicar; segundo leitor em janela externa.

---

## REQ-DOS-003

**Enunciado:** Fechar um dossier é um botão explícito, não um automático a cada mensagem.

**Origem:** docs/origem/plano.md — «Dossier de prova»

**Critérios de aceitação:**

1. **Dado** uma conversa com prova, **quando** o utilizador não carrega em fechar dossier, **então** não é criado um fecho/fotografia automática só por haver novas mensagens.
2. **Dado** o mesmo contexto, **quando** o utilizador activa o botão de fechar dossier, **então** a fotografia é gravada (REQ-DOS-004..006).

**Não pede:** fecho agendado; múltiplos dossiers automáticos por mensagem.

---

## REQ-DOS-004

**Enunciado:** O fecho grava no mesmo SQLite uma fotografia que não volta a correr modelos: perguntas e as frases que ficaram no ecrã; para cada frase, o trecho literal, ficheiro, página, offsets, caixas do highlight e a pontuação do juiz.

**Origem:** docs/origem/plano.md — «Dossier de prova»

**Critérios de aceitação:**

1. **Dado** um dossier acabado de fechar, **quando** se lê o registo no SQLite, **então** contém as perguntas, as frases mostradas, e por frase o trecho literal, ficheiro, página, offsets, caixas (quando existirem) e pontuação do juiz.
2. **Dado** esse dossier, **quando** é reaberto, **então** a visualização não dispara EmbeddingGemma, juiz nem E2B para reconstruir a prova.

**Não pede:** reindexar documentos no fecho; incluir prosa filtrada que nunca apareceu no ecrã.

---

## REQ-DOS-005

**Enunciado:** A fotografia inclui o SHA-256 dos bytes do ficheiro nesse momento.

**Origem:** docs/origem/plano.md — «Dossier de prova»

**Critérios de aceitação:**

1. **Dado** um dossier fechado que cita ficheiros, **quando** se inspecciona a fotografia, **então** cada fonte citada tem o SHA-256 dos bytes no momento do fecho.

**Não pede:** armazenamento de uma segunda cópia completa do PDF dentro do dossier; assinatura criptográfica externa.

---

## REQ-DOS-006

**Enunciado:** A fotografia inclui data e as versões do EmbeddingGemma, do juiz (incluindo o LoRA, se houver) e do E2B.

**Origem:** docs/origem/plano.md — «Dossier de prova»

**Critérios de aceitação:**

1. **Dado** um dossier fechado, **quando** se lê a fotografia, **então** há carimbo de data e identificadores de versão do EmbeddingGemma, do juiz (com indicação de LoRA se aplicável) e do E2B usados na altura.

**Não pede:** versionar a UI da app no dossier; diff automático entre versões de modelo.

---

## REQ-DOS-007

**Enunciado:** Reabrir lê a fotografia. Se o ficheiro em disco tiver outro hash, o dossier mostra que a fonte mudou depois do fecho, e a prova antiga mantém-se.

**Origem:** docs/origem/plano.md — «Dossier de prova»

**Critérios de aceitação:**

1. **Dado** um dossier fechado e o ficheiro fonte inalterado, **quando** o utilizador reabre o dossier, **então** vê a prova da fotografia.
2. **Dado** o mesmo dossier e o ficheiro em disco com SHA-256 diferente do gravado, **quando** o utilizador reabre, **então** há indicação observável de que a fonte mudou, e os trechos/pontuações da fotografia antiga continuam legíveis.

**Não pede:** reescrever a prova com o ficheiro novo; apagar o dossier quando o hash muda.

---

## REQ-DOS-008

**Enunciado:** Exportar escreve um Markdown para ler e um JSON com os mesmos campos, para arquivo.

**Origem:** docs/origem/plano.md — «Dossier de prova»; «Interface»

**Critérios de aceitação:**

1. **Dado** um dossier fechado, **quando** o utilizador exporta, **então** obtém um ficheiro Markdown legível (perguntas, frases citadas, ficheiro e página) e um JSON com os mesmos campos da fotografia para arquivo.

**Não pede:** exportar para PDF tipográfico; upload automático do export.
