# Fora de âmbito — `REQ-FOR`

Cada item regista uma exclusão do plano e o comportamento que a implementação **deve** manter. Cumprir o requisito é *não* introduzir o que está fora de âmbito.

## REQ-FOR-001

**Enunciado:** Base vectorial separada e índice aproximado estão fora de âmbito. A implementação mantém SQLite + `sqlite-vec` no mesmo ficheiro e cosseno exacto.

**Origem:** docs/origem/plano.md — «Base vectorial»; «De fora, porque pesa ou muda o modelo»

**Critérios de aceitação:**

1. **Dado** a stack de pesquisa, **quando** se inventariam dependências e processos, **então** não há Qdrant, Chroma, LanceDB, Postgres vectorial, nem Vec1/ANN como caminho de produção; a procura semântica usa cosseno exacto no mesmo SQLite.

**Não pede:** proibir experiências locais não ligadas ao produto; documentar aqui cada alternativa rejeitada em ADR.

---

## REQ-FOR-002

**Enunciado:** Reavaliar a biblioteca inteira em fundo está fora de âmbito. Alertas e jobs só olham para documentos novos indexados (ou fluxos explícitos que não sejam «varrer tudo sozinho»).

**Origem:** docs/origem/plano.md — «De fora, porque pesa ou muda o modelo»; «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** a app em idle com biblioteca grande, **quando** não há documento novo a indexar, **então** não corre um job em fundo que reavalia sozinho todos os documentos para alertas ou highlights.

**Não pede:** impedir reindexação manual pedida pelo utilizador num documento desactualizado.

---

## REQ-FOR-003

**Enunciado:** Média (ou soma) de ficheiros de pesos LoRA está fora de âmbito. O que empilha é o conjunto de correções JSON e um treino a partir do base.

**Origem:** docs/origem/plano.md — «Juntar afinações»; «De fora, porque pesa ou muda o modelo»

**Critérios de aceitação:**

1. **Dado** o fluxo de juntar afinações, **quando** o utilizador importa/exporta, **então** o artefacto é o JSON de correções / treino a partir do base — não uma média de adaptadores LoRA binários.

**Não pede:** recusar ficheiros LoRA soltos com mensagem específica além de não os usar como método de junção.

---

## REQ-FOR-004

**Enunciado:** Encoder de visão está fora de âmbito. EmbeddingGemma corre só texto; visão e áudio não se carregam.

**Origem:** docs/origem/plano.md — «Três papéis, dois residentes»; «De fora, porque pesa ou muda o modelo»

**Critérios de aceitação:**

1. **Dado** o runtime de embedding, **quando** os modelos carregam, **então** não se carrega encoder de visão nem stack de áudio do EmbeddingGemma (OCR de scans usa Tesseract — REQ-ING-006 — não um encoder de visão).

**Não pede:** impedir abrir imagens no leitor; CLIP ou similar.

---

## REQ-FOR-005

**Enunciado:** Outro modelo de decisão (incluindo Jev e clones locais grandes) está fora de âmbito. O juiz é o mmarco-mMiniLMv2 ONNX int8.

**Origem:** docs/origem/plano.md — «Que modelo faz de System One»; «De fora, porque pesa ou muda o modelo»

**Critérios de aceitação:**

1. **Dado** a configuração de System One, **quando** se identifica o decisor de highlight, **então** é o cross-encoder mmarco definido no plano, não Jev via API, nem Qwen ~4B / DeBERTa grande no lugar do juiz.

**Não pede:** bloquear o utilizador de ter outros modelos no disco sem os ligar à app.

---

## REQ-FOR-006

**Enunciado:** Exemplos de respostas no prompt do E2B estão fora de âmbito. O prompt não inclui prosa anterior nem respostas confirmadas como few-shot.

**Origem:** docs/origem/plano.md — «A resposta, sem reaproveitar respostas velhas»; «De fora, porque pesa ou muda o modelo»

**Critérios de aceitação:**

1. **Dado** o montagem do prompt do E2B, **quando** há histórico de respostas e feedback positivo, **então** esse material não entra como exemplos de resposta no prompt.

**Não pede:** impedir o utilizador de colar texto na pergunta; few-shot no juiz.

---

## REQ-FOR-007

**Enunciado:** Fine-tune do E2B está fora de âmbito. O E2B permanece congelado.

**Origem:** docs/origem/plano.md — «Três papéis, dois residentes»; «De fora, porque pesa ou muda o modelo»

**Critérios de aceitação:**

1. **Dado** feedback e treinos da app, **quando** terminam, **então** não há job de fine-tune nem LoRA aplicado ao E2B; só o juiz é treinado (REQ-FBK / REQ-JUI-004).

**Não pede:** impedir download manual de outros checkpoints pelo utilizador fora da app.

---

## REQ-FOR-008

**Enunciado:** Contas, permissões e sincronização estão fora de âmbito. A app permanece local sem identidade remota.

**Origem:** docs/origem/plano.md — «De fora, porque pesa ou muda o modelo»; alinhado a REQ-SEG-003

**Critérios de aceitação:**

1. **Dado** a superfície do produto, **quando** se procura login, papéis de permissão ou sync multi-dispositivo, **então** essas capacidades não existem.

**Não pede:** partilha manual de JSON de correções ou zip de backup entre pessoas (ficheiro local).

---

## REQ-FOR-009

**Enunciado:** Áudio está fora de âmbito (entrada, saída e modelos de áudio).

**Origem:** docs/origem/plano.md — «Três papéis, dois residentes»; «De fora, porque pesa ou muda o modelo»

**Critérios de aceitação:**

1. **Dado** a UI e o runtime, **quando** se inventariam modalidades, **então** não há modo de dictação/voz nem carregamento de pesos de áudio do EmbeddingGemma.

**Não pede:** silenciar sons do sistema operativo; acessibilidade por teclado (REQ-A11).

---

## REQ-FOR-010

**Enunciado:** Geração de procedimentos de ataque está fora de âmbito. A implementação não oferece modo, lente ou fluxo cujo objectivo seja produzir playbooks ofensivos.

**Origem:** docs/origem/plano.md — «De fora, porque pesa ou muda o modelo»; alinhado a REQ-SEG-006

**Critérios de aceitação:**

1. **Dado** os modos da barra e as lentes, **quando** se listam propósitos suportados, **então** não há entrada dedicada a gerar procedimentos de ataque; o produto mantém-se como chat de pesquisa com prova na página.

**Não pede:** classificador de intenção em tempo real sobre todas as perguntas; remoção de documentos do utilizador sobre segurança.
