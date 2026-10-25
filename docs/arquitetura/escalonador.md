# Escalonador de trabalhos pesados

## Regra central

**Um trabalho pesado de cada vez.**

Trabalhos pesados: procura (incluindo correlacionar e lote de lacunas), indexação de um documento, escrita E2B dentro de uma procura, treino LoRA do juiz.

Trabalhos leves (não ocupam o slot pesado): leitura de SQLite para reabrir chat/dossier, servir estáticos, actualizar UI, feedback imediato em disco (sem treino).

## Prioridade da procura

Quando uma procura pede o slot:

1. Indexação em curso **pausa**.
2. Treino LoRA em curso **pausa** (ou cede o slot; a procura usa sempre o ONNX já activo).
3. A procura corre até ao fim (incluindo visita E2B, se houver).
4. No fim, o escalonador **retoma** indexação e/ou treino que estavam em fila.

Verificação: com indexação a decorrer, enviar Enter numa procura → o documento deixa de avançar até a procura terminar; depois a ingestão continua no mesmo documento/fila.

## Fila de ingestão

- Um **documento** de cada vez na fila de indexação.
- SHA-256 na ingestão; se o ficheiro em disco mudar depois, a biblioteca marca-o desactualizado (não responde com índice velho em silêncio).
- Miniaturas geradas **nessa** indexação, uma vez.

## Núcleos de CPU

Seja `N = nproc` (núcleos lógicos visíveis ao processo).

| Recurso | Limite verificável |
| --- | --- |
| Reserva para sistema + UI | Sempre **≥ 2** núcleos livres (não atribuídos a embedding/juiz/E2B em paralelo agressivo) |
| Embedding + juiz durante procura | Correm dentro do orçamento que deixa ≥ 2 livres |
| E2B a escrever | ≤ `N - 2` núcleos |
| LoRA | ≤ **2** núcleos |

Objectivo observável: com o E2B a gerar, o chat continua a responder ao rato/teclado (o browser e o listener Python não ficam sem CPU).

### Exemplos

| `nproc` | E2B máx. | LoRA máx. | Livres mínimos |
| --- | --- | --- | --- |
| 4 | 2 | 2 | 2 |
| 8 | 6 | 2 | 2 |
| 16 | 14 | 2 | 2 |

## Interacção procura ↔ treino

```text
[livre] --treino--> [LoRA ≤2 núcleos]
[LoRA]  --procura chega--> pausa LoRA --> [procura] --> retoma LoRA ou reencaminha
[index] --procura chega--> pausa index --> [procura] --> retoma index
```

Enquanto o LoRA não exportar ONNX novo com sucesso, **todas** as procuras usam o ONNX anterior.

## O que não corre em paralelo

| Par | Permitido? |
| --- | --- |
| Duas procuras pesadas | Não |
| Procura + indexação activa | Não (indexação pausada) |
| Procura + LoRA activo | Não (LoRA pausado) |
| Indexação + LoRA | Não (um slot pesado) |
| Feedback imediato + procura | Sim (feedback é leve; não bloqueia) |
| Servir UI + qualquer pesado | Sim |

## Estados do escalonador (para telemetria/UI)

| Estado | Significado |
| --- | --- |
| `idle` | Sem trabalho pesado |
| `search` | Procura (ou correlacionar / lacunas) a ocupar o slot |
| `index` | Ingestão de um documento |
| `lora` | Treino do juiz |
| `paused_for_search` | Index/LoRA suspensos porque entrou procura |

Se a UI pedir um segundo trabalho pesado enquanto `search`/`index`/`lora`: ver [falhas.md](falhas.md) («fila ocupada»).
