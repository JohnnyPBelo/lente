# Feedback, LoRA e afinações — `REQ-FBK`

## REQ-FBK-001

**Enunciado:** Cada mensagem com highlights relevantes oferece a linha pequena: Acertou, Corrigir, Descartar. Não bloqueia a procura seguinte.

**Origem:** docs/origem/plano.md — «Feedback, só no juiz»

**Critérios de aceitação:**

1. **Dado** uma mensagem com highlights sujeitos a feedback, **quando** a mensagem está no fio, **então** as acções Acertou, Corrigir e Descartar estão disponíveis numa linha discreta.
2. **Dado** feedback ainda não dado, **quando** o utilizador inicia outra procura, **então** a procura seguinte corre sem esperar por Acertou/Corrigir/Descartar.

**Não pede:** modal modal obrigatório; feedback em mensagens só de aviso vazio sem highlights.

---

## REQ-FBK-002

**Enunciado:** Descartar não treina nada.

**Origem:** docs/origem/plano.md — «Feedback, só no juiz»

**Critérios de aceitação:**

1. **Dado** Descartar numa mensagem, **quando** a acção é confirmada, **então** não se criam exemplos de treino positivos nem negativos a partir dessa mensagem, e o juiz/E2B ficam como estavam quanto a pesos.

**Não pede:** apagar a mensagem do fio; impedir correcção posterior via link (REQ-FBK-003).

---

## REQ-FBK-003

**Enunciado:** Um link discreto fica na mensagem para corrigir mais tarde.

**Origem:** docs/origem/plano.md — «Feedback, só no juiz»

**Critérios de aceitação:**

1. **Dado** uma mensagem após Descartar ou sem feedback imediato, **quando** o utilizador procura na mensagem, **então** existe um link discreto que inicia o fluxo Corrigir mais tarde.

**Não pede:** notificação push para corrigir; prazo de expiração do link.

---

## REQ-FBK-004

**Enunciado:** Acertou marca os trechos mostrados como positivos do juiz.

**Origem:** docs/origem/plano.md — «Feedback, só no juiz»

**Critérios de aceitação:**

1. **Dado** Acertou numa mensagem com trechos destacados, **quando** a acção é registada, **então** esses trechos ficam etiquetados como positivos no conjunto de correções do juiz.

**Não pede:** Acertou a alterar o E2B; injectar os trechos no prompt futuro do escritor.

---

## REQ-FBK-005

**Enunciado:** Corrigir: o utilizador procura, abre o leitor, selecciona. As marcas desta resposta ficam negativas; a selecção fica positiva.

**Origem:** docs/origem/plano.md — «Feedback, só no juiz»

**Critérios de aceitação:**

1. **Dado** o fluxo Corrigir iniciado numa mensagem, **quando** o utilizador selecciona o trecho correcto no leitor, **então** as marcas/trechos da resposta original ficam negativos e a selecção fica positiva no conjunto de correções.

**Não pede:** múltiplas selecções obrigatórias; Corrigir sem abrir o leitor quando a prova é só texto colado sem documento (pode haver caminho mínimo, mas o plano assume leitor).

---

## REQ-FBK-006

**Enunciado:** O feedback não muda o E2B. Muda a ordenação e o limiar dos highlights do juiz.

**Origem:** docs/origem/plano.md — «Feedback, só no juiz»

**Critérios de aceitação:**

1. **Dado** Acertou ou Corrigir, **quando** se inspeccionam os artefactos de modelo, **então** não há fine-tune nem alteração de pesos do E2B; há efeito no juiz (imediato e/ou LoRA).

**Não pede:** feedback a mudar prefixos do EmbeddingGemma.

---

## REQ-FBK-007

**Enunciado:** Na hora, uma pergunta muito parecida privilegia trechos confirmados e desce os rejeitados, entre os candidatos que a pesquisa já trouxe. Não se injecta texto no escritor.

**Origem:** docs/origem/plano.md — «Feedback, só no juiz»

**Critérios de aceitação:**

1. **Dado** correções positivas e negativas recentes, **quando** o utilizador faz uma pergunta muito semelhante e a pesquisa devolve candidatos, **então** entre esses candidatos os confirmados sobem e os rejeitados descem na ordenação antes/durante o highlight.
2. **Dado** o mesmo feedback, **quando** o E2B (se activo) gera prosa, **então** o prompt não recebe texto injectado de «respostas correctas» como exemplos.

**Não pede:** alterar o conjunto de candidatos fora do que a pesquisa já trouxe; reindexar a biblioteca.

---

## REQ-FBK-008

**Enunciado:** Quando ninguém está a procurar, um LoRA rank 8 do juiz rejoga todas as correções, com learning rate baixo e puxão para o modelo base.

**Origem:** docs/origem/plano.md — «Feedback, só no juiz»

**Critérios de aceitação:**

1. **Dado** correções pendentes de treino e a máquina livre de procura, **quando** o treino arranca, **então** é um LoRA rank 8 sobre o juiz, a rejogar o conjunto de correções, com learning rate baixo e regularização/puxão para o base.

**Não pede:** LoRA no EmbeddingGemma ou E2B; rank configurável na UI.

---

## REQ-FBK-009

**Enunciado:** O treino LoRA usa no máximo dois núcleos.

**Origem:** docs/origem/plano.md — «Feedback, só no juiz»; «Orçamento da máquina»

**Critérios de aceitação:**

1. **Dado** o LoRA a correr, **quando** se observa a afinidade/limite de CPU do processo de treino, **então** está limitado a no máximo dois núcleos.

**Não pede:** UI para escolher o número de núcleos; treino GPU obrigatório.

---

## REQ-FBK-010

**Enunciado:** Se as correções deixadas de lado (hold-out) piorarem, a troca é rejeitada. No fim aceite, exporta-se de novo o ONNX e o PyTorch sai da memória. Até lá, a procura usa o ONNX anterior.

**Origem:** docs/origem/plano.md — «Feedback, só no juiz»

**Critérios de aceitação:**

1. **Dado** um treino cujo hold-out piora a métrica definida, **quando** o treino termina, **então** o ONNX em produção não é substituído por esse resultado.
2. **Dado** um treino aceite, **quando** termina, **então** um novo ONNX é exportado, o PyTorch do juiz é libertado, e só depois a procura passa a usar o novo ONNX.
3. **Dado** treino em curso ou rejeitado, **quando** o utilizador procura, **então** usa o ONNX anterior estável.

**Não pede:** rollback manual de várias gerações na UI; métricas custom pelo utilizador.

---

## REQ-FBK-011

**Enunciado:** O que se partilha entre pessoas é o conjunto de correções, não a média de ficheiros de pesos LoRA. Pesquisas repetidas sobre o mesmo tema não multiplicam o sinal; pares repetidos contam uma vez.

**Origem:** docs/origem/plano.md — «Juntar afinações»

**Critérios de aceitação:**

1. **Dado** duas correções com o mesmo hash de par, **quando** entram no conjunto de treino, **então** o par é representado uma vez.
2. **Dado** a política de junção, **quando** se importa afinações de outrem, **então** o mecanismo é juntar exemplos e treinar a partir do base — não somar/média de binários LoRA.

**Não pede:** deduplicação semântica fuzzy além do hash de par; marketplace de pesos.

---

## REQ-FBK-012

**Enunciado:** O ficheiro exportado é JSON com a versão do formato, o id do modelo base, e cada correção: pergunta, trecho, etiqueta, lente, e um hash do par. Os trechos são texto dos documentos.

**Origem:** docs/origem/plano.md — «Juntar afinações»

**Critérios de aceitação:**

1. **Dado** correções existentes, **quando** o utilizador exporta correções, **então** o ficheiro é JSON contendo versão do formato, id do modelo base do juiz, e lista de correções com pergunta, trecho, etiqueta, lente e hash do par.

**Não pede:** exportar o adaptador LoRA binário; encriptação do JSON neste requisito.

---

## REQ-FBK-013

**Enunciado:** O ecrã de exportação diz explicitamente que quem exporta está a entregar frases dos documentos.

**Origem:** docs/origem/plano.md — «Juntar afinações»

**Critérios de aceitação:**

1. **Dado** o fluxo Exportar correções, **quando** o ecrã é mostrado, **então** há aviso legível de que o export contém texto/trechos dos documentos.

**Não pede:** redacção automática de PII; anonimização.

---

## REQ-FBK-014

**Enunciado:** Importar mostra a contagem, as lentes e um punhado de perguntas, e só treina depois de o utilizador confirmar.

**Origem:** docs/origem/plano.md — «Juntar afinações»

**Critérios de aceitação:**

1. **Dado** um ficheiro de correções válido, **quando** o utilizador inicia Importar correções, **então** vê contagem, lentes envolvidas e uma amostra de perguntas antes de qualquer treino.
2. **Dado** essa pré-visualização, **quando** o utilizador não confirma, **então** nada do ficheiro é aplicado ao juiz/treino.
3. **Dado** confirmação, **quando** a máquina está livre, **então** o treino junta as correções importadas às locais a partir do modelo base (mesmo pipeline de sempre).

**Não pede:** aplicar pesos ONNX estranhos sem passar por correções; treino durante uma procura activa.

---

## REQ-FBK-015

**Enunciado:** Um ficheiro de outro modelo base é recusado.

**Origem:** docs/origem/plano.md — «Juntar afinações»

**Critérios de aceitação:**

1. **Dado** um JSON de correções cujo id de modelo base não coincide com o juiz instalado, **quando** o utilizador tenta importar, **então** a importação é recusada com erro observável e não mistura os exemplos.

**Não pede:** conversão automática entre bases; mapeamento manual de IDs.

---

## REQ-FBK-016

**Enunciado:** Nada de um import se aplica antes da confirmação — incluindo ficheiros maliciosos que tentem ensinar o juiz ao contrário.

**Origem:** docs/origem/plano.md — «Juntar afinações»

**Critérios de aceitação:**

1. **Dado** um ficheiro de importação ainda não confirmado, **quando** o utilizador procura ou usa o juiz, **então** o comportamento do juiz é o anterior ao import (sem exemplos do ficheiro a afectar ordenação/treino).

**Não pede:** análise antivírus do JSON; sandbox de rede (já é local).

---

## REQ-FBK-017

**Enunciado:** Exportar e Importar correções vivem no estado da aprendizagem no topo da barra lateral — não no menu `+` da barra de escrita.

**Origem:** docs/origem/plano.md — «A barra de escrita»; alinhado a REQ-BAR-012

**Critérios de aceitação:**

1. **Dado** a barra lateral, **quando** o utilizador olha para o estado da aprendizagem no topo, **então** encontra Exportar correções e Importar correções.
2. **Dado** o menu `+`/`/`, **quando** se listam itens, **então** essas acções não estão lá.

**Não pede:** segundo sítio de importação nas definições avançadas.

---

## REQ-FBK-018

**Enunciado:** O treino após import parte do modelo base, junta as correções tuas e as importadas, e corre quando a máquina está livre (pausável por procura — REQ-BUS-012).

**Origem:** docs/origem/plano.md — «Juntar afinações»; «Orçamento da máquina»

**Critérios de aceitação:**

1. **Dado** correções locais e importadas confirmadas, **quando** o treino corre, **então** parte do base e usa o conjunto união (com dedupe de pares).
2. **Dado** treino a decorrer, **quando** chega uma procura, **então** o treino pausa e retoma depois (REQ-BUS-012).

**Não pede:** treinos paralelos por fonte de importação; filas na nuvem.
