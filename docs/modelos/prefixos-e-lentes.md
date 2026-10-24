# MOD-lentes — Prefixos EmbeddingGemma e instruções E2B

A lente de trabalho (pastilha na barra) muda o **prefixo** da query no EmbeddingGemma e, quando há prosa, a **instrução** enviada ao E2B. Não muda o confronto ([confronto.md](confronto.md)).

## Mapa lente / modo → prefixo

| Uso | Prefixo EmbeddingGemma 2 |
| --- | --- |
| Documento (indexação) | `title: {título} \| text: {conteúdo}` |
| Procurar — pesquisa curta (repouso) | `task: search result \| query: …` |
| Lente **investigar** | `task: question answering \| query: …` |
| Lente **acreditação** | `task: question answering \| query: …` |
| Lente **verificar** | `task: fact checking \| query: …` |
| Lente **assessment** | `task: fact checking \| query: …` |

A instrução de prosa **não** entra no texto embutido. Só no E2B.

## Instruções de prosa (só E2B)

Texto fixo, em português de Portugal, prependido ao pacote de trechos da procura. Exemplos sintéticos de tom — não são prompts de sistema genéricos de outro produto.

### Investigar

```
Responde em português de Portugal. Usa só os trechos numerados desta procura.
Cada frase afirmativa termina com a citação [n] do trecho que a sustenta.
Não inventes controlos, datas nem cláusulas que não estejam nos trechos.
Prefere frases curtas e ligadas à prova na página.
```

### Assessment

```
Responde em português de Portugal no registo de assessment: o que o texto afirma, o que falta, e o risco residual só se os trechos o permitirem.
Cada afirmação termina com [n]. Sem [n], não escrevas a frase.
Não emits parecer jurídico nem receita de ataque; resume evidência citada.
```

### Acreditação

```
Responde em português de Portugal no registo de acreditação: requisitos, evidências e lacunas só com base nos trechos.
Cada frase de conformidade ou não conformidade termina com [n].
Não completes requisitos com conhecimento geral fora dos trechos.
```

### Verificar

```
Responde em português de Portugal. Trata a pergunta como verificação factual contra os trechos.
Marca o que está suportado, o que está contradito e o que está ausente; cada afirmação com [n].
Não suavizes contradições; cita o trecho.
```

### Procurar (sem lente especializada / pesquisa curta)

Quando o modo é Procurar e a lente de trabalho não impõe assessment/acreditação/verificar/investigar, usa:

```
Responde em português de Portugal com base só nos trechos numerados.
Cada frase termina com [n]. Se os trechos não chegarem, não completes com conhecimento externo.
```

## Alerta e lacunas — sem E2B

| Modo | Embedding + FTS + juiz | E2B |
| --- | --- | --- |
| Procurar / Correlacionar (com prosa) | Sim | Sim (visita), com instrução da lente |
| Confrontar | Juiz + cosseno (sem prosa E2B) | **Não** |
| **Alerta** | Sim (só frases de documentos novos) | **Não** |
| **Lacunas** | Sim (lista encontrado / fraco / ausente) | **Não** |

A lente ainda muda o **prefixo** (e o critério de «encontrado/fraco/ausente» via juiz) em alerta e lacunas; **não** dispara geração de prosa.

## Fora deste contrato

- Meter a prosa da lente no embedding.
- Lentes personalizadas pelo utilizador neste marco.
- E2B a gerar a classificação do confronto.

## Origem

[docs/origem/plano.md](../origem/plano.md) — «A barra de escrita», «Pesquisa, sem modelo a mais»; fecho «Lentes → prefixos» em [docs/LEITURA.md](../LEITURA.md).
