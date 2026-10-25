# PLN-17: Importar e exportar correcções

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Exportar JSON de correções (versão formato, id modelo base, pares pergunta/trecho/etiqueta/lente/hash); importar com pré-visualização (contagem, lentes, amostra de perguntas), confirmação obrigatória, dedupe por hash, recusa se modelo base diferente; treino junta locais+importadas a partir do base.
**Fronteira:** o que NÃO entra neste plano — exportar binário LoRA; aplicar import sem confirmação; UI dentro do menu `+` (fica no estado da aprendizagem no topo da lateral).
**Ficheiros futuros:**
- `engine/feedback/exportar_correcoes.py`
- `engine/feedback/importar_correcoes.py`
- `engine/feedback/schema_correcoes.py` — validação (alinhar a `docs/dados/correcoes.schema.json`)
- `apps/ui/src/components/aprendizagem/ExportarCorrecoes.tsx`
- `apps/ui/src/components/aprendizagem/ImportarCorrecoes.tsx`
- `tests/feedback/test_export_import.py`
- `tests/fixtures/feedback/correcoes.exemplo.json` — sintético
**Teste que falha primeiro:** `tests/feedback/test_export_import.py` — export produz JSON com `formato_versao` e `modelo_base_id`; import do mesmo ficheiro com `confirmar=False` **não** grava pares; com `confirmar=True` grava; segundo import não duplica hashes; ficheiro com `modelo_base_id` outro → `ModeloBaseIncompativel`.

## Passos

- [ ] Escrever testes (acima) com fixture sintética em PT.
- [ ] Commit: `test(feedback): falha sem export/import de correções`.
- [ ] Implementar export; ecrã avisa que se entregam frases dos documentos.
- [ ] Implementar import: parse → preview DTO → confirm → upsert dedupe.
- [ ] UI no topo da lateral: «Exportar correções», «Importar correções».
- [ ] Após import confirmado, agendar LoRA quando livre (mesmo pipeline PLN-16).
- [ ] Fazer passar.
- [ ] Commit: `feat(feedback): exportar e importar correções JSON`.
- [ ] Teste: ficheiro malicioso estruturalmente inválido → 400 sem side effects.
- [ ] Commit: `test(feedback): import inválido sem efeitos`.
- [ ] Commit de fecho.

## Notas para o executor

- O que empilha é o conjunto de correções, não média de adapters.
- Exemplos sintéticos apenas — não copiar documentos reais.
