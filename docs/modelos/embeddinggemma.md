# MOD-emb — EmbeddingGemma 2 (só texto)

**Papel:** encontrar. Congelado e residente.

## Identidade

| Campo | Valor |
| --- | --- |
| Hugging Face | [`google/embeddinggemma-2`](https://huggingface.co/google/embeddinggemma-2) |
| Papel no Lente | Embedding de blocos (indexação) e de consultas (pesquisa) |
| Parâmetros carregados | **270M, só texto** (`vision_config=None`, `audio_config=None`) |
| Visão / áudio / vídeo | **Não se carregam** |
| Vector nativo | 768 dimensões |
| Vector no Lente | **256** (corte Matryoshka do de 768) **+ normalização L2** |
| Residência | Residente |
| Fine-tune | Não |

## Matryoshka e normalização

1. Obter o embedding de 768d.
2. Cortar às primeiras **256** dimensões.
3. **Renormalizar L2** depois do corte (obrigatório; um prefixo de um vector unitário deixa de ser unitário).
4. Queries e documentos usam a **mesma** dimensão (256).

Sem renormalização, o cosseno degrada em silêncio.

## Dtypes

| Hardware | Dtype |
| --- | --- |
| CPU | **float32** |
| GPU (quando existir e suportar) | **bfloat16** |
| Qualquer sítio | **float16 proibido** |

A ficha do modelo e o plano registam que float16 produz NaN ou embeddings degradados sem erro explícito. Não há caminho float16 no código.

## Prefixos (resumo)

Tabela completa e mapeamento às lentes: [prefixos-e-lentes.md](prefixos-e-lentes.md).

| Uso | Prefixo |
| --- | --- |
| Documento (indexação) | `title: {título} \| text: {conteúdo}` |
| Procurar (pesquisa curta) | `task: search result \| query: …` |
| Investigar, acreditação | `task: question answering \| query: …` |
| Verificar, assessment | `task: fact checking \| query: …` |

Sem título: `title: none | text: {conteúdo}`.

## Disco

Tecto do artefacto de runtime só-texto: cerca de **2 GB**. Não se descarregam encoders de visão nem de áudio.

## Unidade de embedding

Bloco de cerca de **500 tokens** do tokenizador do EmbeddingGemma, sobreposição de **50**. A unidade de highlight e de julgamento continua a ser a **frase** (offsets/caixas na ingestão) — ver fecho em [docs/LEITURA.md](../LEITURA.md).

## Licença (ficha do modelo)

A ficha Hugging Face / documentação EmbeddingGemma 2 publica os pesos sob **Apache License 2.0**, permitindo afinar e implantar nos teus projectos. Isto cobre os **pesos** deste modelo; o Apache-2.0 do repositório Lente cobre texto e código da app, não substitui a ficha HF. Detalhe: [licencas.md](licencas.md).

## Fora deste contrato

- Carregar torres de visão ou áudio.
- Vectores 128d / 512d / 768d no índice de produção (o Lente fixa 256d).
- Fine-tune ou LoRA do EmbeddingGemma.
- float16.

## Origem

[docs/origem/plano.md](../origem/plano.md) — «Três papéis, dois residentes», «Pesquisa, sem modelo a mais»; fechos em [docs/LEITURA.md](../LEITURA.md).
