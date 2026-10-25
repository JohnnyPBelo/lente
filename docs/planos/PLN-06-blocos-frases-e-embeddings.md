# PLN-06: Blocos, frases e embeddings (EmbeddingGemma 256d)

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Cortar texto indexado em blocos (~500 tokens EmbeddingGemma, overlap 50), segmentar frases com offsets/caixas, gerar embeddings 256d normalizados (float32) e persistir; modelo residente e congelado.
**Fronteira:** o que NÃO entra neste plano — FTS5/pesquisa (PLN-07), juiz, E2B, visão/áudio do EmbeddingGemma, fine-tune do embedding.
**Ficheiros futuros:**
- `engine/embeddings/__init__.py`
- `engine/embeddings/carregar.py` — load EmbeddingGemma 2 texto-only; caminho local se HF falhar
- `engine/embeddings/prefixos.py` — `title: … | text: …` para documentos
- `engine/embeddings/cortar.py` — blocos 500 / overlap 50
- `engine/embeddings/frases.py` — segmentação + offsets
- `engine/embeddings/indexar.py` — orquestra documento → blocos/frases/vectores
- `engine/embeddings/dispositivo.py` — CPU float32; GPU acelera o mesmo código
- `tests/embeddings/test_cortar.py`
- `tests/embeddings/test_embedding_dim.py`
- `tests/fixtures/embeddings/paragrafo_longo.txt`
**Teste que falha primeiro:** `tests/embeddings/test_cortar.py` — dado texto cujo tokenizador produz >600 tokens, `cortar_blocos` devolve ≥2 blocos; overlap ≈50 tokens entre fim do bloco i e início do i+1; cada bloco ≤~500 tokens (± margem documentada).

## Passos

- [ ] Escrever testes de corte sem carregar o modelo (tokenizador stub ou tokenizer real leve).
- [ ] Commit: `test(embeddings): falha sem corte 500/50`.
- [ ] Implementar `cortar.py` com o tokenizador oficial do EmbeddingGemma.
- [ ] Implementar segmentação de frases; herdar caixas da ingestão quando existirem.
- [ ] Teste de dimensão: embedding de uma frase → `numpy` shape `(256,)`, L2 ≈ 1.0, dtype float32, sem NaN.
- [ ] Commit: `test(embeddings): dimensão 256 e norma`.
- [ ] Implementar carga do modelo; política de falha HF = mensagem com caminho para pesos manuais (sem impedir arranque da app — integração plena em PLN-21).
- [ ] Prefixar documentos: `title: {título} | text: {conteúdo}`.
- [ ] Gravar `blocos`, `frases`; vectores na estrutura sqlite-vec (ou tabela temporária se PLN-07 ainda não ligou a extensão — preferir interface `guardar_vector(bloco_id, vec)`).
- [ ] Fazer passar com modelo real ou mock injectável nos testes unitários + um teste de integração marcado.
- [ ] Commit: `feat(embeddings): blocos, frases e EmbeddingGemma 256d`.
- [ ] Teste: float16 path **não** usado em CPU (evitar NaN — ADR dtypes).
- [ ] Miniatura: gerar imagem pequena na indexação se PDF/imagem.
- [ ] Commit: `test(embeddings): float32 e miniatura na indexação`.
- [ ] Commit de fecho.

## Notas para o executor

- Visão e áudio do modelo **não** se carregam.
- Unidade de embedding = bloco; unidade de highlight/juízo = frase (ADR-012 / LEITURA.md).
