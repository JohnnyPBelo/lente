# Ordem de trabalho PLN-15

Fonte: `docs/planos/PLN-15-leque-e-leitor.md`. Implementação completa do leque, leitor, citações e rotas HTTP de documento.

## Objectivo

Após resposta com documentos: miniaturas; um doc abre leitor; vários abrem leque → escolha → cresce até leitor; Escape/minimizar recolhe; leitor com scroll contínuo, highlights literais, zoom, sumário, cópia de citação, fixar trecho; serif no texto; `prefers-reduced-motion` encurta sem remover leque/leitor.

## Fronteira

o que NÃO entra neste plano — dossier (PLN-18), feedback LoRA (PLN-16), OCR novo.

## Teste que falha primeiro, no plano

`reg-cht-004.test.tsx` — com 3 miniaturas, hover/foco (desktop) revela leque; click na 2.ª chama `onAbrir(docId)`; com `prefers-reduced-motion: reduce`, animações curtas/ausentes mas leque e abertura permanecem disponíveis.

## Dependências

Fundidos em `main` antes desta implementação:

- PLN-13 — chrome
- PLN-14 — barra

## Ficheiros criados / alterados

- `apps/ui/src/components/leque/Leque.tsx`, `Miniatura.tsx`
- `apps/ui/src/components/leitor/Leitor.tsx`, `Highlights.tsx`, `Sumario.tsx`, `Ferramentas.tsx`
- `apps/ui/src/components/chat/CitacaoLink.tsx`, `MensagemComDocumentos.tsx`, `RespostaComDocumentos.tsx`
- `engine/api/rotas_documento.py` — HTTP-reader-* e HTTP-chat-pin-excerpt
- `engine/api/app.py` — registo das rotas de documento
- `apps/ui/src/lib/api.ts`, `copy.ts` — cliente e copy do leitor
- `apps/ui/src/styles/global.css`, `tokens.css` — serif, leque, superfície sólida
- Testes REG listados abaixo; `tests/api/test_fixar_trecho.py`

Não se alterou `App.tsx`, chrome PLN-13 nem `barra/` (PLN-14). A composição entra via `RespostaComDocumentos` / testes; a barra já expõe `trechoConfrontarExterno` para a bolha Confrontar.

## Não tocar (respeitado)

- `apps/ui/src/components/barra/` e chrome PLN-13, incluindo `App.tsx`
- `engine/api/rotas_chat.py` e `rotas_modos.py`
- `engine/dossier/`, `engine/feedback/lora.py`
- `docs/verificacao/cobertura.md`, `tests/regressao/{test_suite,apoio,exigir_agora}.py`, `scripts/regressao.sh`
- `docs/origem/plano.md`, `data/`, pesos

Excepção: linhas no fim de `tests/regressao/manifesto.txt`.

## Requisitos fechados

| REQ | REG |
| --- | --- |
| REQ-BUS-011 | REG-BUS-011 |
| REQ-JUI-003 | REG-JUI-003 |
| REQ-RES-009 | REG-RES-009 |
| REQ-CHT-003…008 | REG-CHT-003…008 |
| REQ-LEI-001…011 | REG-LEI-001…011 |
| REQ-DOS-001…002 | REG-DOS-001…002 |

## Testes de regressão (manifesto)

- `apps/ui/src/components/chat/reg-bus-011.test.tsx`
- `apps/ui/src/components/leitor/reg-jui-003.test.tsx`
- `apps/ui/src/components/chat/reg-res-009.test.tsx`
- `apps/ui/src/components/leque/reg-cht-003.test.tsx`
- `apps/ui/src/components/leque/reg-cht-004.test.tsx`
- `apps/ui/src/components/leitor/reg-cht-005.test.tsx`
- `apps/ui/src/components/leque/reg-cht-006.test.tsx`
- `apps/ui/src/components/leque/reg-cht-007.test.tsx`
- `apps/ui/src/components/leitor/reg-cht-008.test.tsx`
- `apps/ui/src/components/leitor/reg-lei-001.test.tsx` … `reg-lei-011.test.tsx` (exceto 008)
- `tests/api/test_fixar_trecho.py::test_reg_lei_008`
- `apps/ui/src/components/chat/reg-dos-001.test.tsx`
- `apps/ui/src/components/chat/reg-dos-002.test.tsx`

Também, se em falta em `main`: `tests/api/test_modos.py::test_reg_confronto_c1` … `c5`.

## Definição de pronto

- [x] Comportamento implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` verde (a confirmar antes do merge).
- [x] Manifesto cresceu com os identificadores desta ordem.
- [x] Sem ficheiros de pesos no git.
- [x] Texto visível de `docs/interface/copy.md`.

## Paralelo

Pode avançar ao lado de PLN-16, PLN-18 e PLN-19 nos seus componentes.
