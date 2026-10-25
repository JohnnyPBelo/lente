# Ordem de trabalho PLN-19

Fonte: `docs/planos/PLN-19-alertas.md`. Implementação no ramo `pln-19-alertas`.

## Objectivo

Criar até 10 alertas; grupo Alertas na lateral; fio próprio; ao indexar documento novo o juiz avalia só essas frases; mensagem com miniatura; antigos não revistos sozinhos; interruptor no topo; sem E2B.

## Fronteira

Não reavalia a biblioteca em fundo; sem E2B; sem correlacionar via alerta.

## Fecho

- [x] Limite de dez com `LimiteAlertas` / `limite_alertas`.
- [x] Avaliação só com `novo=True` / gancho `avaliar_apos_indexacao`.
- [x] UI `GrupoAlertas` e `FioAlerta` (interruptor).
- [x] Prefixo de lente na consulta ao juiz.
- [x] `scripts/regressao.sh` verde com os REG deste plano no manifesto.
- [x] Sem pesos no git; copy de `docs/interface/copy.md`.
