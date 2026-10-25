# Glossário

Termos do plano de origem, com o sítio onde a regra está fechada.

| Termo | Significado neste projecto | Onde |
| --- | --- | --- |
| Lente (produto) | A app. Chat local com prova na página. | `docs/origem/plano.md` |
| Lente (controlo) | Pastilha da barra: investigar, assessment, acreditação, verificar. Muda a instrução da procura, do alerta e das lacunas. Não muda o confronto. | ADR-009, `docs/modelos/prefixos-e-lentes.md` |
| EmbeddingGemma | Quem encontra. 270M só texto, vector 256, residente, congelado. | `docs/modelos/embeddinggemma.md` |
| Juiz | Cross-encoder mMARCO 118M em ONNX int8. Decide o highlight e a segunda porta. Não é o Jev. | ADR-003, `docs/modelos/juiz.md` |
| E2B | Gemma 4 E2B QAT Q4. Escreve e sai da memória. Congelado. | ADR-004, `docs/modelos/e2b.md` |
| Duas portas | A frase tem `[n]` de um trecho do pacote, e o juiz considera-a fiel a esse trecho. Só então aparece. | ADR-011, `docs/modelos/duas-portas.md` |
| Highlight | Intervalo literal do ficheiro, pintado pelo código. Unidade: a frase, com offsets e caixas. | ADR-012 |
| Bloco | Cerca de 500 tokens do tokenizador do EmbeddingGemma, sobreposição 50. Unidade do vector. | ADR-012 |
| Fusão | Rank recíproco entre FTS5 e cosseno, no código. | `docs/modelos/fusao-limiar-platt.md` |
| Identificador literal | Cláusula, CVE, sigla, código escrito à letra. Não cai no chão de cosseno. Continua a passar pelo juiz. | ADR-014 |
| Leque | Miniaturas dos documentos com highlight. Um documento abre o leitor; vários abrem o leque. | `docs/interface/chat-e-leque.md` |
| Leitor | O documento inteiro, com as marcas. Minimizar ou Escape volta à miniatura. | `docs/interface/leitor.md` |
| Dossier | Fotografia da conversa, fechada por botão. Não volta a correr modelos. | `docs/dados/dossier.schema.json` |
| Correcção | Par pergunta–trecho com etiqueta, lente e hash. O que se exporta. Não é o ficheiro do LoRA. | `docs/dados/correcoes.schema.json` |
| LoRA | Rank 8 só no juiz, quando a máquina está livre, no máximo dois núcleos. Troca recusada se o holdout piorar. | ADR-005, ADR-006 |
| Alerta | Até dez. O juiz olha só para as frases do documento acabado de indexar. | `docs/requisitos/alertas.md` |
| Lacunas | Uma mensagem, uma linha por controlo. Encontrado, fraco ou ausente. Sem E2B. Não se repete sozinha. | `docs/requisitos/barra.md` |
| Confrontar | Três leituras: concordam, contradizem-se, assuntos diferentes. Função do juiz nas duas direcções e do cosseno. | ADR-010, `docs/modelos/confronto.md` |
| Diário | Registo local só de acrescentar. Sem contas e sem rede. | `docs/requisitos/diario.md` |
| Cópia de segurança | Zip da pasta `data/`, no sítio escolhido. Sem nuvem. | `docs/requisitos/backup.md` |
| System One / Jev | Papel de decisão rápida. No Lente fá-lo o juiz mMARCO. O Jev não se instala. | ADR-003 |
