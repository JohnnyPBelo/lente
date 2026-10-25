# Execução PLN-21

Fonte: `docs/planos/PLN-21-estados-vazios-a11y-e-comando-unico.md`. Implementado neste ramo: comando único, estados vazios, a11y reduced-motion, rotas de modelos e regressões REG-MOD/VAZ/A11/SEG/FOR listadas abaixo.

## Objectivo

Cobrir estados vazios observáveis (biblioteca sem ficheiros, modelo a descarregar, prosa toda filtrada, página sem texto, URL recusada, conversa nova, procura sem documentos); acessibilidade (`prefers-reduced-motion` encurta sem remover leque/leitor); um comando sobe UI+motor em `127.0.0.1:4317`; piso Python 3.11+ / Node 22 / 16 GB documentado; se HF bloquear download, a app abre e diz onde pôr o ficheiro.

## Fronteira

Não entrou: novas funcionalidades de produto; Electron; segundo modo GPU; reimplementação de portas/SSRF/LoRA/dossier.

## O que ficou no código

| Área | Ficheiros |
| --- | --- |
| Comando único | `engine/cli.py`, `scripts/lente`, `pyproject.toml` (`lente = engine.cli:main`) |
| Pesos / orientação | `engine/runtime/pesos.py`, `piso.py`, `residentes.py` |
| HTTP modelos + health | `engine/api/rotas_modelos.py`; `engine/api/app.py` (health dinâmico, placeholder `/`) |
| Estados vazios | `apps/ui/src/components/vazios/*.tsx` + `reg-vaz-001.test.tsx` |
| A11y | `apps/ui/src/a11y/focos.ts`, `PercursoMotion.tsx`, `reg-a11-001.test.tsx`, `reg-seg-003.test.tsx` |
| Docs | `README.md` («Como correr»), este ficheiro |

O harness `PercursoMotion` prova REG-A11-001 sem reescrever leque/leitor (PLN-15). `AreaChat` passa a usar `ConversaNova`.

## Não tocar (respeitado)

- `docs/verificacao/cobertura.md`
- `tests/regressao/test_suite.py`, `apoio.py`, `exigir_agora.py`, `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos
- Ficheiros de leque/leitor (PLN-15)

Excepção: linhas acrescentadas **só no fim** de `tests/regressao/manifesto.txt`.

## Requisitos fechados

- `REQ-MOD-001` → `REG-MOD-001`
- `REQ-MOD-002` → `REG-MOD-002`
- `REQ-MOD-007` → `REG-MOD-007`
- `REQ-MOD-008` → `REG-MOD-008`
- `REQ-MOD-009` → `REG-MOD-009`
- `REQ-VAZ-001` → `REG-VAZ-001`
- `REQ-A11-001` → `REG-A11-001`
- `REQ-SEG-003` → `REG-SEG-003`
- `REQ-FOR-008` → `REG-FOR-008`
- `REQ-FOR-009` → `REG-FOR-009`

## Testes no manifesto (fim)

- `tests/runtime/test_comando_unico.py::test_reg_mod_001`
- `tests/runtime/test_piso.py::test_reg_mod_002`
- `tests/runtime/test_comando_unico.py::test_reg_mod_007`
- `tests/runtime/test_comando_unico.py::test_reg_mod_008`
- `tests/runtime/test_residentes.py::test_reg_mod_009`
- `apps/ui/src/components/vazios/reg-vaz-001.test.tsx`
- `apps/ui/src/a11y/reg-a11-001.test.tsx`
- `apps/ui/src/a11y/reg-seg-003.test.tsx`
- `tests/runtime/test_sem_contas.py::test_reg_for_008`
- `tests/runtime/test_sem_contas.py::test_reg_for_009`

## Definição de pronto

- [x] Comportamento dentro da fronteira
- [x] Manifesto só acrescentado no fim
- [x] Sem pesos no git
- [x] Copy dos vazios alinhada a `docs/interface/copy.md`
- [ ] `scripts/regressao.sh` verde (verificar antes do merge)
