# PLN-11: Escritor E2B e duas portas

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Carregar Gemma 4 E2B QAT Q4 só na visita de escrita; gerar prosa a partir dos trechos aprovados pelo juiz; filtrar por duas portas (citação `[n]` válida + fidelidade do juiz); sem histórico de respostas no prompt; miniaturas/excertos podem existir sem E2B.
**Fronteira:** o que NÃO entra neste plano — fine-tune E2B, exemplos de respostas no prompt, HTTP/UI completos, LoRA do juiz.
**Ficheiros futuros:**
- `engine/resposta/__init__.py`
- `engine/resposta/e2b.py` — carga/descarga GGUF, limite de núcleos
- `engine/resposta/prompt.py` — montar contexto só com trechos desta procura (+ página aberta se aplicável)
- `engine/resposta/porta1_citacao.py` — exige `[n]` de trecho do pacote
- `engine/resposta/porta2_fiel.py` — juiz frase↔trecho citado
- `engine/resposta/filtrar.py` — pipeline das portas; se zero frases → excertos ou vazio
- `tests/resposta/test_portas.py`
- `tests/resposta/test_prompt.py`
**Teste que falha primeiro:** `tests/resposta/test_portas.py` — frase sem `[n]` é descartada; frase com `[99]` inexistente no pacote é descartada; frase com `[1]` cujo texto contradiz o trecho 1 (score juiz baixo) é descartada; frase fiel com `[1]` sobrevive.

## Passos

- [ ] Escrever testes das duas portas com juiz mockado.
- [ ] Commit: `test(resposta): falha sem duas portas`.
- [ ] Implementar parse de citações `[n]` e validação contra o pacote.
- [ ] Porta 2: chamar juiz; limiar de fidelidade documentado.
- [ ] `prompt.py`: **não** incluir respostas anteriores nem exemplos confirmados; perguntas anteriores só para reescrever query (função separada).
- [ ] Stub E2B nos unitários; teste de integração marcado para GGUF.
- [ ] Garantir descarga da memória após resposta (API `libertar()` verificável em teste com mock).
- [ ] Sem E2B: devolver excertos + ids de documentos para miniaturas.
- [ ] Commit: `feat(resposta): E2B visita e filtro das duas portas`.
- [ ] Teste: prosa só depois das portas — nenhuma frase «provisória» na estrutura de resultado.
- [ ] Commit: `test(resposta): sem prosa provisória`.
- [ ] Commit de fecho.

## Notas para o executor

- Não descarregar os ~11 GB de pesos de treino BF16 do E2B.
- Alerta e lacunas não chamam E2B (LEITURA.md) — respeitar quando a API os expuser.
