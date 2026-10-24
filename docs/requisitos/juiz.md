# Juiz — `REQ-JUI`

## REQ-JUI-001

**Enunciado:** O System One local é o cross-encoder [`cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`](https://huggingface.co/cross-encoder/mmarco-mMiniLMv2-L12-H384-v1) (118M, Apache 2.0, mMARCO incluindo português). No dia a dia corre o ONNX int8 já publicado (~120 MB). Não é o Jev e não traz a calibração do Jev.

**Origem:** docs/origem/plano.md — «Que modelo faz de System One»

**Critérios de aceitação:**

1. **Dado** a app com modelos prontos, **quando** se identifica o binário/residente do juiz, **então** é o ONNX int8 do mmarco-mMiniLMv2-L12-H384-v1 (não pesos Jev nem clone Qwen/DeBERTa grande no lugar do juiz).

**Não pede:** calibração idêntica ao Jev da TypeSafe; segundo juiz em paralelo.

---

## REQ-JUI-002

**Enunciado:** O juiz é residente e leve; o seu papel é decisão rápida sem prosa: esta frase responde ou não (decide o highlight).

**Origem:** docs/origem/plano.md — «Que modelo faz de System One»; «Três papéis, dois residentes»

**Critérios de aceitação:**

1. **Dado** a app pronta para procurar, **quando** corre uma procura, **então** o juiz ONNX está residente (não é carregado só no fim da prosa).
2. **Dado** candidatos da pesquisa, **quando** o juiz avalia, **então** o resultado por frase é uma decisão de passar/não passar (pontuação), sem gerar a prosa da resposta.

**Não pede:** o juiz a escrever a mensagem do chat; o juiz a substituir o EmbeddingGemma.

---

## REQ-JUI-003

**Enunciado:** Quem pinta o highlight é o código. Cada marca é um intervalo literal do ficheiro (offsets/caixas da ingestão), não texto regenerado.

**Origem:** docs/origem/plano.md — «Três papéis, dois residentes»

**Critérios de aceitação:**

1. **Dado** uma frase deixada passar pelo juiz, **quando** o highlight é mostrado no leitor, **então** a marca corresponde ao intervalo literal gravado na ingestão (offsets e, quando existirem, caixas), byte/carácter a byte/carácter do trecho fonte.

**Não pede:** o modelo a devolver coordenadas de pixel inventadas; fuzzy match que altere o texto marcado.

---

## REQ-JUI-004

**Enunciado:** A pontuação do juiz ajusta-se com o feedback do utilizador, e só nesse modelo (não no E2B nem no EmbeddingGemma).

**Origem:** docs/origem/plano.md — «Que modelo faz de System One»; «Feedback, só no juiz»

**Critérios de aceitação:**

1. **Dado** feedback Acertou/Corrigir aplicado, **quando** uma procura semelhante volta a correr (efeito imediato e/ou após LoRA — ver REQ-FBK), **então** a ordenação ou o limiar dos highlights reflecte esse feedback no juiz.
2. **Dado** o mesmo feedback, **quando** se inspeccionam EmbeddingGemma e E2B, **então** os seus pesos congelados não foram alterados por esse feedback.

**Não pede:** feedback a injectar texto no escritor; calibração Jev.

---

## REQ-JUI-005

**Enunciado:** O PyTorch só entra para um LoRA do juiz depois de feedback, e sai da memória quando o treino acaba. Até exportar o novo ONNX, a procura usa o ONNX anterior.

**Origem:** docs/origem/plano.md — «Três papéis, dois residentes»; «Feedback, só no juiz»

**Critérios de aceitação:**

1. **Dado** treino LoRA a decorrer, **quando** se observa a memória de modelos, **então** o stack PyTorch do juiz está presente só durante esse treino.
2. **Dado** o treino terminado (aceite ou rejeitado), **quando** a memória é libertada, **então** o PyTorch do juiz já não permanece residente para a procura quotidiana.
3. **Dado** treino ainda não exportado ou rejeitado, **quando** o utilizador procura, **então** o ONNX em uso é o anterior estável.

**Não pede:** PyTorch residente permanente; média de vários adaptadores LoRA (ver REQ-FOR-003).
