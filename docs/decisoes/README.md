# Decisões de arquitectura (ADRs)

Registo das decisões de arquitectura do Lente. Cada ADR aponta para [docs/origem/plano.md](../origem/plano.md), a fonte de verdade.

| ID | Título | Resumo |
| --- | --- | --- |
| [ADR-001](ADR-001-tres-papeis-dois-residentes.md) | Três papéis, dois residentes | EmbeddingGemma e juiz ONNX residem; E2B visita. |
| [ADR-002](ADR-002-sqlite-fts5-sqlite-vec.md) | SQLite único com FTS5 e sqlite-vec | Um ficheiro, cosseno exacto; sem Vec1/Qdrant/Chroma/LanceDB/Postgres. |
| [ADR-003](ADR-003-juiz-mmarco-em-vez-de-jev.md) | Juiz mmarco-mMiniLMv2 no lugar do Jev | Sem pesos Jev; cabe em 16 GB. |
| [ADR-004](ADR-004-e2b-congelado.md) | E2B congelado | Sem prosa anterior, sem exemplos, sem fine-tune do escritor. |
| [ADR-005](ADR-005-feedback-so-no-juiz.md) | Feedback só no juiz | LoRA rank 8; exportar correcções JSON, não média de LoRA. |
| [ADR-006](ADR-006-um-trabalho-pesado.md) | Um trabalho pesado de cada vez | E2B ≤ nproc−2; LoRA ≤ 2 núcleos. |
| [ADR-007](ADR-007-dtypes.md) | Dtypes dos modelos | EmbeddingGemma float32 CPU / bfloat16 GPU; float16 excluído; juiz ONNX int8. |
| [ADR-008](ADR-008-superficie-local.md) | Superfície local | Sem contas, sem rede de sync; só 127.0.0.1:4317. |
| [ADR-009](ADR-009-lentes-prefixos.md) | Lentes → prefixos EmbeddingGemma 2 | Prefixo por lente; prosa da lente só no E2B; alerta/lacunas sem E2B. |
| [ADR-010](ADR-010-confronto-deterministico.md) | Confronto determinístico | Duas direcções do juiz + cosseno; sem modelo novo. |
| [ADR-011](ADR-011-frase-depois-das-duas-portas.md) | Frase só depois das duas portas | Miniaturas podem vir primeiro; sem prosa provisória. |
| [ADR-012](ADR-012-blocos-e-frases.md) | Blocos e frases | ~500 tokens overlap 50 para embedding; frase com offsets/caixas. |
| [ADR-013](ADR-013-servidor-python-ui.md) | Um só servidor Python | Serve UI construída; Node 22 só build; sem Electron. |
| [ADR-014](ADR-014-identificador-literal.md) | Identificador literal | Fura o chão de cosseno; continua sujeito ao juiz. |
| [ADR-015](ADR-015-escala-cosseno-exacto.md) | Escala e cosseno exacto | Milhares de docs; exacto mantém-se mesmo fora de ms; sem índice aproximado. |
| [ADR-016](ADR-016-fora-de-ambito.md) | Fora de âmbito | Lista do que o plano exclui de propósito. |
