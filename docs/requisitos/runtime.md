# Runtime e modelos — `REQ-MOD`

## REQ-MOD-001

**Enunciado:** Um comando sobe a UI em `127.0.0.1:4317` e o motor Python. Um só servidor: o motor Python escuta nesse endereço e serve a UI já construída. Node 22 constrói a UI; não há Electron.

**Origem:** docs/origem/plano.md — «Como corre»; fecho de lacuna (LEITURA — «Um só servidor»)

**Critérios de aceitação:**

1. **Dado** o ambiente com dependências instaladas, **quando** o utilizador corre o comando de arranque documentado, **então** a UI fica acessível em `http://127.0.0.1:4317` e o motor Python está a servir.
2. **Dado** a stack em execução, **quando** se inspecciona o empacotamento, **então** não há runtime Electron; a UI foi construída com Node 22 e é servida pelo processo Python.

**Não pede:** binding em `0.0.0.0`; HTTPS local obrigatório; app store packaging.

---

## REQ-MOD-002

**Enunciado:** Piso de ambiente: Python 3.11+, Node 22, 16 GB de RAM alvo.

**Origem:** docs/origem/plano.md — «Como corre»; introdução

**Critérios de aceitação:**

1. **Dado** a documentação/arranque, **quando** se verificam os requisitos mínimos declarados, **então** constam Python 3.11+, Node 22 e alvo de 16 GB de RAM.
2. **Dado** versões abaixo do piso (quando detectáveis no arranque), **quando** a app inicia, **então** há falha ou aviso observável em vez de corrida silenciosa indefinida.

**Não pede:** suporte oficial a menos de 16 GB; macOS/Windows/Linux com instaladores assinados neste requisito.

---

## REQ-MOD-003

**Enunciado:** EmbeddingGemma, juiz e E2B deixam sempre pelo menos dois núcleos livres para o sistema e para a interface. O E2B, quando escreve, fica limitado a esses núcleos (nproc−2), para o chat continuar a responder ao rato.

**Origem:** docs/origem/plano.md — «Orçamento da máquina»

**Critérios de aceitação:**

1. **Dado** embedding, juiz ou E2B a correr trabalho pesado, **quando** se observa o limite de CPU, **então** ficam pelo menos dois núcleos livres para SO/UI.
2. **Dado** o E2B a gerar, **quando** o utilizador move o rato/interage com o chat, **então** a UI continua a responder (o E2B não satura todos os núcleos).

**Não pede:** afinação fina por workload na UI; GPU a contar como «núcleos» neste requisito.

---

## REQ-MOD-004

**Enunciado:** Um trabalho pesado de cada vez: procura pausa indexação e treino e retoma no fim (ver REQ-BUS-012). LoRA do juiz ≤ 2 núcleos (REQ-FBK-009).

**Origem:** docs/origem/plano.md — «Orçamento da máquina»

**Critérios de aceitação:**

1. **Dado** indexação ou LoRA activos, **quando** uma procura começa, **então** esse trabalho pausa e retoma depois da procura.
2. **Dado** LoRA a treinar, **quando** corre, **então** respeita o máximo de dois núcleos.

**Não pede:** prioridade real-time do SO; cancelamento destrutivo da fila de indexação.

---

## REQ-MOD-005

**Enunciado:** A GPU, se existir, acelera o mesmo código. Não há um segundo modo.

**Origem:** docs/origem/plano.md — introdução; «Orçamento da máquina»

**Critérios de aceitação:**

1. **Dado** uma máquina com GPU utilizável, **quando** os modelos correm, **então** usam o mesmo pipeline de código (não um «modo GPU» separado na UX).
2. **Dado** uma máquina só CPU, **quando** a app corre, **então** o mesmo fluxo funcional está disponível (sem exigir GPU).

**Não pede:** suporte a todas as GPUs do mercado; fallback cloud.

---

## REQ-MOD-006

**Enunciado:** Disco aproximado dos três papéis: cerca de 2 GB (EmbeddingGemma), 0,5 GB (juiz) e 3 GB (E2B). Não se descarregam os 11 GB de pesos de treino do E2B.

**Origem:** docs/origem/plano.md — «Orçamento da máquina»

**Critérios de aceitação:**

1. **Dado** a instalação/download dos modelos de runtime, **quando** se listam os artefactos obtidos, **então** não está incluído o pacote de ~11 GB de pesos de treino do E2B.
2. **Dado** os três modelos de runtime presentes, **quando** se estima o espaço, **então** está na ordem de grandeza 2 + 0,5 + 3 GB (não dezenas de GB além disso por pesos de treino).

**Não pede:** medição exacta ao megabyte em todos os SO; compressão adicional pelo utilizador.

---

## REQ-MOD-007

**Enunciado:** Se a licença Hugging Face bloquear um download, a app abre e diz onde pôr o ficheiro.

**Origem:** docs/origem/plano.md — «Como corre»; alinhado a REQ-ING-011

**Critérios de aceitação:**

1. **Dado** um download de modelo bloqueado por licença HF, **quando** a app arranca, **então** a UI abre e mostra indicação clara do local/caminho onde colocar o ficheiro em falta.

**Não pede:** contornar a licença; download automático com token guardado na nuvem.

---

## REQ-MOD-008

**Enunciado:** Sem o E2B, o chat segue com excertos e miniaturas (runtime degradado gracioso).

**Origem:** docs/origem/plano.md — «Como corre»; alinhado a REQ-RES-008

**Critérios de aceitação:**

1. **Dado** E2B ausente e juiz/embedding presentes, **quando** o utilizador procura com resultados, **então** obtém excertos e miniaturas sem crash por falta do escritor.

**Não pede:** gerar prosa por outro modelo substituto.

---

## REQ-MOD-009

**Enunciado:** Residente numa procura: sistema, browser, EmbeddingGemma em float32 (CPU), juiz em int8, SQLite. O E2B é visita. Float16 no embedding está excluído (NaN).

**Origem:** docs/origem/plano.md — «Orçamento da máquina»; «Três papéis, dois residentes»

**Critérios de aceitação:**

1. **Dado** uma procura em curso (sem contar a janela em que o E2B escreve), **quando** se listam modelos residentes, **então** EmbeddingGemma e juiz ONNX int8 estão presentes e o E2B não é residente permanente.
2. **Dado** EmbeddingGemma em CPU, **quando** embute, **então** usa float32 (não float16).

**Não pede:** documentar aqui o dtype exacto em GPU além do plano/ADR; carregar visão/áudio.
