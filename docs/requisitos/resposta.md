# Resposta e portas — `REQ-RES`

## REQ-RES-001

**Enunciado:** O E2B vê os trechos que o juiz deixou passar nesta procura, com ficheiro e página, e o texto dessas páginas. Não vê a biblioteca inteira.

**Origem:** docs/origem/plano.md — «A resposta, sem reaproveitar respostas velhas»

**Critérios de aceitação:**

1. **Dado** uma procura com N trechos aprovados pelo juiz, **quando** o E2B gera prosa, **então** o pacote de contexto contém esses trechos (ficheiro, página, texto) e não a biblioteca completa.

**Não pede:** o E2B a indexar; RAG sobre todos os documentos sem filtro do juiz.

---

## REQ-RES-002

**Enunciado:** Respostas anteriores não entram no prompt do E2B, nem como exemplo nem como fine-tune. O E2B não vê a prosa que escreveu antes nem exemplos de respostas confirmadas.

**Origem:** docs/origem/plano.md — «Três papéis, dois residentes»; «A resposta, sem reaproveitar respostas velhas»

**Critérios de aceitação:**

1. **Dado** um chat com respostas anteriores do assistente, **quando** se monta o prompt do E2B para uma nova procura, **então** esse prompt não inclui a prosa das respostas anteriores nem exemplos de respostas confirmadas.

**Não pede:** apagar o histórico visível no fio; fine-tune do E2B (proibido — REQ-FOR-007).

---

## REQ-RES-003

**Enunciado:** Se o leitor estiver aberto e a pergunta for sobre essa página, essa página entra também no contexto do E2B.

**Origem:** docs/origem/plano.md — «A resposta, sem reaproveitar respostas velhas»

**Critérios de aceitação:**

1. **Dado** o leitor aberto numa página concreta e uma pergunta do utilizador referente a essa página, **quando** o E2B gera a resposta, **então** o texto dessa página faz parte do pacote de contexto além dos trechos aprovados da procura.

**Não pede:** incluir o documento inteiro quando a pergunta não é sobre a página aberta; incluir todas as páginas do PDF aberto.

---

## REQ-RES-004

**Enunciado:** Porta 1 — cada frase da prosa tem de acabar com `[n]` a citar um trecho que estava no pacote desta procura. Sem isso, a frase sai.

**Origem:** docs/origem/plano.md — «A resposta, sem reaproveitar respostas velhas»

**Critérios de aceitação:**

1. **Dado** uma frase gerada pelo E2B sem citação `[n]` válida do pacote, **quando** passam as portas, **então** essa frase não aparece no fio.
2. **Dado** uma frase com `[n]` cujo `n` não corresponde a trecho do pacote, **quando** passam as portas, **então** essa frase não aparece no fio.

**Não pede:** reescrita automática da frase para acrescentar `[n]`; citações a documentos fora do pacote.

---

## REQ-RES-005

**Enunciado:** Porta 2 — o juiz compara a frase com o trecho citado; se não for fiel, a frase sai.

**Origem:** docs/origem/plano.md — «A resposta, sem reaproveitar respostas velhas»

**Critérios de aceitação:**

1. **Dado** uma frase com `[n]` válido mas cujo conteúdo não é fiel ao trecho citado segundo o juiz, **quando** passa a porta 2, **então** a frase não aparece no fio.

**Não pede:** o utilizador a calibrar a porta 2 por frase na mesma mensagem; segunda geração automática até passar.

---

## REQ-RES-006

**Enunciado:** A prosa só aparece no fio depois de passar as duas portas. As miniaturas podem aparecer primeiro. Não há prosa provisória a ser apagada.

**Origem:** fecho de lacuna (LEITURA — «Frase só depois das duas portas»); docs/origem/plano.md — «A resposta, sem reaproveitar respostas velhas»

**Critérios de aceitação:**

1. **Dado** uma procura em curso com E2B, **quando** as miniaturas já estão visíveis mas as portas ainda não concluíram, **então** não se mostra prosa que depois desaparece.
2. **Dado** frases que passaram as duas portas, **quando** a mensagem completa, **então** só essas frases (além de excertos/miniaturas conforme o caso) estão no fio.

**Não pede:** atrasar as miniaturas até às portas; streaming de prosa não filtrada.

---

## REQ-RES-007

**Enunciado:** Se nenhuma frase sobreviver às portas, ficam os excertos e as miniaturas, ou só o aviso de vazio. As miniaturas aparecem primeiro quando há documentos.

**Origem:** docs/origem/plano.md — «A resposta, sem reaproveitar respostas velhas»; «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** uma procura em que todas as frases falham as portas mas há trechos/documentos candidatos mostráveis, **quando** a mensagem termina, **então** o utilizador vê excertos e/ou miniaturas (miniaturas primeiro) sem prosa inventada.
2. **Dado** uma procura sem nada acima do limiar, **quando** a mensagem termina, **então** aparece o aviso de vazio e não há documentos/miniaturas a fingir resultados.

**Não pede:** forçar o E2B a regenerar até haver prosa; esconder os excertos quando a prosa falha.

---

## REQ-RES-008

**Enunciado:** Sem o E2B disponível, o chat segue com excertos e miniaturas (não bloqueia a prova na página).

**Origem:** docs/origem/plano.md — «Como corre»

**Critérios de aceitação:**

1. **Dado** EmbeddingGemma e juiz disponíveis mas E2B em falta ou não carregado, **quando** o utilizador faz uma procura com hits, **então** a mensagem mostra excertos e miniaturas e permite abrir o leitor nas citações/trechos, sem exigir o E2B.

**Não pede:** descarregar automaticamente os 11 GB de pesos de treino; modo «só nuvem» para prosa.

---

## REQ-RES-009

**Enunciado:** Quando há prosa, fica presa aos trechos (cada frase citada liga à prova). O contexto de saída do E2B mantém-se o do modelo de base, mais os trechos desta procura.

**Origem:** docs/origem/plano.md — «Três papéis, dois residentes»; «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** frases que passaram as duas portas, **quando** o utilizador clica na citação de uma frase, **então** abre o leitor na página/highlight correspondente (ver também REQ-DOS-001/002).

**Não pede:** alargar o contexto do E2B com a biblioteca ou com chats outros.

---

## REQ-RES-010

**Enunciado:** O E2B sobe para escrever a resposta e desce a seguir (visita). Fica congelado — sem fine-tune.

**Origem:** docs/origem/plano.md — «Três papéis, dois residentes»

**Critérios de aceitação:**

1. **Dado** uma resposta com E2B concluída, **quando** a geração termina, **então** o E2B deixa de ocupar o papel de residente (é libertado/descarregado da RAM de trabalho conforme o runtime, ficando EmbeddingGemma e juiz como residentes da procura).
2. **Dado** feedback do utilizador, **quando** se inspeccionam os pesos do E2B, **então** não foram fine-tunados por esse feedback.

**Não pede:** E2B sempre residente; quantização diferente da QAT Q4 definida no plano.

---

## REQ-RES-011

**Enunciado:** Alerta e lacunas não chamam o E2B; a instrução de prosa de cada lente só entra no E2B quando há prosa (modos que a usam).

**Origem:** fecho de lacuna (LEITURA — «Lentes → prefixos EmbeddingGemma 2»)

**Critérios de aceitação:**

1. **Dado** o modo Alerta ou Lacunas, **quando** o utilizador envia, **então** o pipeline não carrega/chama o E2B para gerar prosa livre.
2. **Dado** uma procura com E2B no modo Procurar (ou correlacionar com prosa), **quando** há lente activa, **então** a instrução de prosa dessa lente pode entrar no prompt do E2B, distinta dos prefixos de embedding.

**Não pede:** prosa no confronto (o confronto tem três leituras fixas — ver REQ-BAR-008); E2B em alertas.
