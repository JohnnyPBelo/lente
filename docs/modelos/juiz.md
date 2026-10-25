# MOD-juiz — Cross-encoder mmarco (porta de highlight)

**Papel:** decidir o highlight. Decisão rápida sem prosa: esta frase responde ou não. Residente e leve.

## Identidade

| Campo | Valor |
| --- | --- |
| Hugging Face | [`cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`](https://huggingface.co/cross-encoder/mmarco-mMiniLMv2-L12-H384-v1) |
| Parâmetros | ~118M |
| Treino | mMARCO (inclui português) |
| Runtime diário | **ONNX int8** já publicado no repo HF |
| Tamanho ONNX int8 | cerca de **119 MB** |
| Residência | Residente (ONNX) |
| Licença dos pesos | **Apache 2.0** (ficha do modelo) |

Não é o Jev da TypeSafe e não traz a calibração dele. A pontuação afina-se com o feedback do utilizador, **só neste modelo**.

## Ficheiros ONNX int8

Pasta `onnx/` no Hugging Face. Em produção o Lente usa:

| Arquitectura | Ficheiro |
| --- | --- |
| x86-64 com AVX-512 VNNI (preferido) | `model_qint8_avx512_vnni.onnx` |
| arm64 | `model_qint8_arm64.onnx` |

Ambos ~119 MB. A escolha é automática pela máquina; o papel e a API de pontuação são os mesmos.

## Papel: porta de highlight

1. A pesquisa (embedding + FTS5 + RRF) traz candidatos.
2. O juiz pontua pares **pergunta ↔ frase** (ou, nas duas portas da prosa, **frase gerada ↔ trecho citado**).
3. Só o que passa o limiar ([fusao-limiar-platt.md](fusao-limiar-platt.md)) merece highlight.
4. **Quem pinta** o highlight é o código: intervalo literal do ficheiro (offsets/caixas da ingestão), não texto regenerado.

O juiz **não** escreve a resposta do chat. Isso é o E2B, depois das [duas portas](duas-portas.md).

## PyTorch só para LoRA

| Momento | Stack |
| --- | --- |
| Procura / highlight / portas / confronto | ONNX int8 residente |
| Treino LoRA (após feedback, máquina livre) | PyTorch **entra**, treina rank 8, exporta ONNX de novo |
| Fim do treino | PyTorch **sai da memória** |

Até o novo ONNX estar aceite, a procura usa o ONNX anterior. Detalhe de feedback e exportação de correcções fica nos requisitos `REQ-FBK-*`; este contrato só fixa: PyTorch não é residente do dia a dia.

## Fora deste contrato

- Manter PyTorch do juiz residente.
- Substituir por Jev, Qwen ~4B ou DeBERTa grande.
- Afinação do E2B ou do EmbeddingGemma com o mesmo feedback.
- Média de vários ficheiros LoRA (o que empilha são as correcções JSON).

## Origem

[docs/origem/plano.md](../origem/plano.md) — «Que modelo faz de System One», «Três papéis, dois residentes», «Feedback, só no juiz».
