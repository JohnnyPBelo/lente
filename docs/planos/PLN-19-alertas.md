# PLN-19: Alertas

> Para workers agenticos: implementar tarefa a tarefa. Passos usam `- [ ]`.

**Objetivo:** Criar até 10 alertas a partir do modo Alerta; grupo «Alertas» na barra lateral; cada alerta é um fio; ao indexar documento **novo**, o juiz avalia só frases desse documento; se passar limiar, mensagem no fio com miniatura; documentos antigos não são revistos sozinhos; interruptor no topo do fio desliga.
**Fronteira:** o que NÃO entra neste plano — reavaliar biblioteca inteira em fundo; E2B nos alertas; correlacionar via alerta.
**Ficheiros futuros:**
- `engine/alertas/__init__.py`
- `engine/alertas/criar.py`
- `engine/alertas/avaliar_documento.py` — chamado no fim da indexação
- `engine/alertas/limite.py` — máx. 10
- `apps/ui/src/components/alertas/GrupoAlertas.tsx`
- `apps/ui/src/components/alertas/FioAlerta.tsx`
- `tests/alertas/test_limite.py`
- `tests/alertas/test_avaliar_novo.py`
**Teste que falha primeiro:** `tests/alertas/test_avaliar_novo.py` — com alerta activo cuja query casa com frase de um documento acabado de indexar (juiz mock alto), cria-se mensagem no fio do alerta com `documento_id` e miniatura; reindexar o **mesmo** doc antigo sem ser «novo» na política → não dispara; alerta desligado → não dispara.

## Passos

- [x] Teste limite: 11.º alerta → erro `LimiteAlertas`.
- [x] Teste avaliar novo (acima).
- [x] Commit: `test(alertas): falha sem avaliação pós-indexação`.
- [x] Hook no fim de indexação bem-sucedida de documento novo.
- [x] Sem E2B; só juiz + excerto/miniatura.
- [x] UI grupo sob conversas; interruptor no fio.
- [x] Lente do alerta aplica prefixo (PLN-14).
- [x] Fazer passar.
- [x] Commit: `feat(alertas): vigia pós-indexação até 10`.
- [x] Teste: indexação pausada por procura não perde o gancho — avalia quando a indexação conclui.
- [x] Commit: `test(alertas): avaliação após retoma da indexação`.
- [x] Commit de fecho.

## Notas para o executor

- «Documentos antigos não são revistos sozinhos» — política explícita nos testes.
