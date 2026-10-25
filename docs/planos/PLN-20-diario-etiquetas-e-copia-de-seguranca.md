# PLN-20: Diário, etiquetas e cópia de segurança

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Diário local append-only (procuras, documentos abertos, feedback, fechos de dossier); etiquetas manuais em documentos com filtro na biblioteca (sugestão de tipo por embedding continua só sugestão); acção de backup: zip da pasta `data/` para caminho escolhido, sem nuvem.
**Fronteira:** o que NÃO entra neste plano — contas, rede de sync, edição/apagamento do diário, backup incremental remoto.
**Ficheiros futuros:**
- `engine/diario/__init__.py`
- `engine/diario/escrever.py` — só INSERT
- `engine/diario/ler.py` — leitura paginada
- `engine/biblioteca/etiquetas.py`
- `engine/biblioteca/filtrar.py` — etiquetas + tipo manual
- `engine/backup/zip_data.py`
- `apps/ui/src/components/biblioteca/Etiquetas.tsx`
- `apps/ui/src/components/biblioteca/ListaVirtualizada.tsx`
- `apps/ui/src/components/backup/CopiaSeguranca.tsx`
- `tests/diario/test_append.py`
- `tests/biblioteca/test_etiquetas.py`
- `tests/backup/test_zip_data.py`
**Teste que falha primeiro:** `tests/diario/test_append.py` — após registar procura e feedback, `ler_diario` devolve as entradas em ordem; tentativa de `UPDATE`/`DELETE` via API do módulo falha ou não existe (só append); `tests/backup/test_zip_data.py` — zip contém o `.sqlite` de fixture e extrai bit-a-bit igual.

## Passos

- [ ] Testes diário append + backup zip + etiquetas filtram lista.
- [ ] Commit: `test: falha sem diário, etiquetas e backup zip`.
- [ ] Implementar eventos de diário nos pontos do motor (procura, abrir doc, feedback, fechar dossier).
- [ ] Etiquetas N:N; filtro biblioteca; tipo manual vs `tipo_sugerido`.
- [ ] Lista virtualizada na UI para milhares de ficheiros.
- [ ] Backup: diálogo de caminho; zip `data/`; sem upload.
- [ ] Fazer passar.
- [ ] Commit: `feat: diário append-only, etiquetas e cópia zip`.
- [ ] Teste: sugestão de tipo não sobrescreve `tipo` manual.
- [ ] Commit: `test(biblioteca): tipo manual prevalece`.
- [ ] Commit de fecho.

## Notas para o executor

- Sem contas nem rede para estas funcionalidades.
- SHA-256 na ingestão já marca desactualizado — garantir que a biblioteca expõe esse estado na lista.
