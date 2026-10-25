# Execução PLN-17

Fonte: `docs/planos/PLN-17-importar-e-exportar-correcoes.md`. Dependência PLN-16 fundida em `main`.

## Objectivo

Exportar JSON de correções (chaves do esquema); importar com pré-visualização, confirmação obrigatória, dedupe por hash e recusa de outro modelo base; treino junta locais+importadas a partir do base.

## Entregue

- `engine/feedback/exportar_correcoes.py`, `importar_correcoes.py`, `schema_correcoes.py`
- `apps/ui/src/components/aprendizagem/{ExportarCorrecoes,ImportarCorrecoes,EstadoAprendizagem}.tsx`
- `tests/feedback/test_export_import.py` e testes Vitest REG-BAR-012 / REG-FBK-013 / REG-FBK-017
- Linhas REG no fim de `tests/regressao/manifesto.txt`

## Notas

O ficheiro valida contra `docs/dados/correcoes.schema.json`. Nada se aplica antes da confirmação. O ecrã de exportação usa `export.warning` de `copy.md`. Não se exporta nem importa binário LoRA.
