# PLN-18: Dossier

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Fechar dossier sob pedido (botão, não automático): fotografia no SQLite com perguntas, frases, trechos literais, ficheiro, página, offsets, caixas, score do juiz, SHA-256, data e versões dos modelos; reabrir sem correr modelos; se hash do ficheiro mudou, avisar mantendo prova antiga; export Markdown + JSON.
**Fronteira:** o que NÃO entra neste plano — reindexação automática ao detectar mudança; cloud sync.
**Ficheiros futuros:**
- `engine/dossier/__init__.py`
- `engine/dossier/fechar.py`
- `engine/dossier/reabrir.py`
- `engine/dossier/exportar.py` — Markdown + JSON
- `engine/dossier/integridade.py` — comparar SHA actual vs fotografia
- `apps/ui/src/components/dossier/BotaoFecharDossier.tsx`
- `apps/ui/src/components/dossier/VistaDossier.tsx`
- `tests/dossier/test_fechar_reabrir.py`
- `tests/dossier/test_export.py`
**Teste que falha primeiro:** `tests/dossier/test_fechar_reabrir.py` — fechar conversa fixture grava fotografia; apagar pesos/mocks de modelos e `reabrir` devolve as mesmas frases/offsets sem chamar embedding/juiz/E2B; alterar bytes do ficheiro fonte → flag `fonte_alterada=True` e prova antiga intacta.

## Passos

- [ ] Testes fechar/reabrir/integridade.
- [ ] Commit: `test(dossier): falha sem fotografia congelada`.
- [ ] Implementar fecho: só frases que passaram as duas portas; incluir versões EmbeddingGemma, juiz(+LoRA se houver), E2B.
- [ ] Reabrir: ler JSON/tabela; UI read-only com links para leitor nas caixas gravadas.
- [ ] Export: `.md` legível + `.json` arquivo (schema dados).
- [ ] Botão explícito «Fechar dossier»; nunca auto por mensagem.
- [ ] Fazer passar.
- [ ] Commit: `feat(dossier): fecho, reabrir e export`.
- [ ] Teste: citação no dossier abre leitor na página/highlight gravados.
- [ ] Commit: `test(dossier): prova na página após fecho`.
- [ ] Commit de fecho.

## Notas para o executor

- Distingue a app de um chat que esquece a origem da frase.
- Exemplos sintéticos no teste.
