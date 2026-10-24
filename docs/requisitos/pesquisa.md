# Pesquisa — `REQ-BUS`

## REQ-BUS-001

**Enunciado:** O EmbeddingGemma 2 (270M, só texto) é o modelo de recuperação: vector de 256 dimensões (corte Matryoshka do de 768, depois normalizado), congelado e residente. Visão e áudio não se carregam. Em CPU corre em float32 (float16 produz NaN).

**Origem:** docs/origem/plano.md — «Três papéis, dois residentes»

**Critérios de aceitação:**

1. **Dado** a app pronta para procurar, **quando** se inspecciona o runtime residente, **então** o EmbeddingGemma texto está carregado e permanece residente durante a procura.
2. **Dado** uma procura, **quando** se obtêm vectores de documento ou de query, **então** a dimensionalidade efectiva usada na pesquisa é 256 e os vectores estão normalizados para cosseno.
3. **Dado** execução em CPU, **quando** o embedding corre, **então** o dtype activo não é float16 (usa-se float32).

**Não pede:** carregar visão ou áudio do EmbeddingGemma; fine-tune do embedding; segundo modelo de embedding.

---

## REQ-BUS-002

**Enunciado:** As queries e documentos usam os prefixos do EmbeddingGemma 2 conforme a lente: documento `title: {título} | text: {conteúdo}`; procurar curto `task: search result | query: …`; investigar e acreditação `task: question answering | query: …`; verificar e assessment `task: fact checking | query: …`.

**Origem:** docs/origem/plano.md — «Pesquisa, sem modelo a mais»; fecho de lacuna (LEITURA — «Lentes → prefixos EmbeddingGemma 2»)

**Critérios de aceitação:**

1. **Dado** um bloco a embutir na indexação, **quando** se forma o texto de entrada do EmbeddingGemma, **então** começa com o prefixo `title: … | text: …`.
2. **Dado** a lente «investigar» ou «acreditação» activa no modo Procurar, **quando** se embute a query, **então** o prefixo é `task: question answering | query: …`.
3. **Dado** a lente «verificar» ou «assessment», **quando** se embute a query, **então** o prefixo é `task: fact checking | query: …`.
4. **Dado** procura curta no modo Procurar (lente de pesquisa curta / repouso de search result), **quando** se embute a query, **então** o prefixo é `task: search result | query: …`.

**Não pede:** a instrução de prosa da lente no embedding (essa só entra no E2B); alerta e lacunas a chamar o E2B.

---

## REQ-BUS-003

**Enunciado:** O FTS5 no mesmo SQLite apanha o termo exacto (número de cláusula, CVE, sigla, identificador) e produz candidatos que se juntam aos do embedding.

**Origem:** docs/origem/plano.md — «Pesquisa, sem modelo a mais»; «Base vectorial»

**Critérios de aceitação:**

1. **Dado** um documento indexado que contém um identificador literal distinto (ex.: um código CVE ou número de cláusula), **quando** o utilizador procura exactamente por esse termo, **então** o trecho correspondente entra no conjunto de candidatos FTS5 antes do juiz.

**Não pede:** o FTS5 a substituir o juiz; ranking FTS5 sozinho a pintar highlights.

---

## REQ-BUS-004

**Enunciado:** Texto exacto (FTS5) e semântica (embedding) fundem-se no código por fusão de rank recíproco (RRF). O juiz continua a filtrar o que se marca.

**Origem:** docs/origem/plano.md — «Base vectorial»

**Critérios de aceitação:**

1. **Dado** candidatos vindos de FTS5 e de embedding para a mesma procura, **quando** a fusão corre, **então** a lista fundida usa rank recíproco (RRF) e alimenta o juiz; highlights só aparecem após o juiz deixar passar.

**Não pede:** pesos RRF configuráveis pelo utilizador na UI; segunda passagem de embedding após RRF.

---

## REQ-BUS-005

**Enunciado:** A pesquisa semântica é cosseno exacto, não aproximada. Não se usa índice aproximado (incluindo Vec1 do SQLite).

**Origem:** docs/origem/plano.md — «Base vectorial»; fecho de lacuna (LEITURA — «Escala»)

**Critérios de aceitação:**

1. **Dado** um corpus com milhares de documentos e vectores de 256 dimensões, **quando** se corre uma procura semântica, **então** o vizinho correcto por cosseno exacto não é omitido por ANN/HNSW/aproximação.
2. **Dado** a configuração da app, **quando** se inspecciona a stack de pesquisa, **então** não está activo o índice aproximado Vec1 nem outro ANN.

**Não pede:** trocar para aproximado se o varrimento deixar de caber em milissegundos (a correcção mantém-se exacta — ver REQ-DES-001 e REQ-FOR-001).

---

## REQ-BUS-006

**Enunciado:** A extensão `sqlite-vec` corre no mesmo processo e escreve os vectores no mesmo ficheiro SQLite que documentos, FTS5, chats, feedback e dossiers (`data/`). Sobrevive a reinícios; uma cópia do ficheiro leva o índice.

**Origem:** docs/origem/plano.md — «Base vectorial»

**Critérios de aceitação:**

1. **Dado** documentos indexados, **quando** se copia o ficheiro SQLite de `data/` e se reabre a app com essa cópia, **então** vectores e FTS5 estão disponíveis sem reindexar.
2. **Dado** o processo da app, **quando** a pesquisa vectorial corre, **então** não há segundo processo de base vectorial (Qdrant, Chroma, LanceDB, Postgres, etc.).

**Não pede:** replicação multi-ficheiro; sync remoto do SQLite.

---

## REQ-BUS-007

**Enunciado:** Um código ou identificador escrito à letra fura o chão de cosseno (não é descartado só por semelhança semântica média); continua sujeito ao juiz.

**Origem:** docs/origem/plano.md — «Pesquisa, sem modelo a mais»; fecho de lacuna (LEITURA — «Identificador literal»)

**Critérios de aceitação:**

1. **Dado** um trecho candidato com match literal de identificador e cosseno abaixo do limiar semântico habitual, **quando** a lista de candidatos é filtrada antes do juiz, **então** esse trecho não é eliminado pelo chão de cosseno.
2. **Dado** o mesmo trecho, **quando** o juiz o avalia, **então** ainda pode ser rejeitado pelo juiz (o bypass não força highlight).

**Não pede:** bypass do juiz; lista branca manual de identificadores na UI.

---

## REQ-BUS-008

**Enunciado:** As perguntas anteriores no mesmo chat servem só para completar uma procura de seguimento. A frase reescrita vai à pesquisa; não é mostrada como conhecimento; a resposta nova tem de citar trechos desta volta.

**Origem:** docs/origem/plano.md — «A resposta, sem reaproveitar respostas velhas»

**Critérios de aceitação:**

1. **Dado** um chat com contexto (ex.: pergunta anterior sobre um tema) e uma pergunta curta de seguimento («e o controlo de acessos?»), **quando** o utilizador envia, **então** a pesquisa recebe uma query reescrita completa, não só a frase curta isolada sem contexto.
2. **Dado** essa procura de seguimento, **quando** a resposta é mostrada, **então** as citações referem trechos obtidos nesta volta (não prosa de respostas anteriores como fonte).

**Não pede:** mostrar a query reescrita como mensagem do assistente; fine-tune com histórico.

---

## REQ-BUS-009

**Enunciado:** O limiar de relevância/highlight é visível na interface.

**Origem:** docs/origem/plano.md — «Pesquisa, sem modelo a mais»

**Critérios de aceitação:**

1. **Dado** a app em uso normal de procura, **quando** o utilizador consulta o estado da procura ou das afinações do juiz, **então** o limiar em vigor é mostrado de forma legível (valor ou controlo visível), não só em logs.

**Não pede:** o utilizador poder forçar highlights abaixo do limiar sem passar pelo fluxo de correcção.

---

## REQ-BUS-010

**Enunciado:** Com correções suficientes, a escala de Platt calcula-se nos exemplos do utilizador e ajusta a interpretação das pontuações do juiz.

**Origem:** docs/origem/plano.md — «Pesquisa, sem modelo a mais»

**Critérios de aceitação:**

1. **Dado** um conjunto de correções do utilizador acima do mínimo definido pela implementação para Platt, **quando** a calibração corre (em idle / após treino conforme o runtime), **então** a escala de Platt passa a ser aplicada às pontuações do juiz nas procuras seguintes.
2. **Dado** correções insuficientes, **quando** se procura, **então** a app não finge calibração Platt: usa o comportamento base sem escala inventada.

**Não pede:** calibração online a cada clique; UI de hiperparâmetros Platt.

---

## REQ-BUS-011

**Enunciado:** No modo Correlacionar, o resultado usa três cores (conceito A, conceito B, relação) e os documentos entram no mesmo leque da mensagem.

**Origem:** docs/origem/plano.md — «Pesquisa, sem modelo a mais»; «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** Conceito A e Conceito B enviados no modo Correlacionar, **quando** a mensagem de resultado aparece, **então** há distinção visual em três cores para A, B e a relação, e as miniaturas dos documentos relevantes entram no leque dessa mensagem.

**Não pede:** um quarto modelo só para correlação; layout diferente do fio de chat habitual.

---

## REQ-BUS-012

**Enunciado:** Uma procura pausa a indexação e o treino em curso e retoma-os no fim, para um trabalho pesado de cada vez.

**Origem:** docs/origem/plano.md — «Orçamento da máquina»

**Critérios de aceitação:**

1. **Dado** indexação ou treino LoRA a decorrer, **quando** o utilizador inicia uma procura, **então** esse trabalho pesado é pausado enquanto a procura (e a resposta associada) corre.
2. **Dado** a procura terminada, **quando** há trabalho pausado, **então** a indexação ou o treino retomam sem o utilizador ter de os relançar manualmente.

**Não pede:** fila de várias procuras em paralelo; cancelamento permanente da indexação só por ter procurado uma vez.
