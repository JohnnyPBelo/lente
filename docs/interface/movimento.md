# Movimento

Origem: `docs/origem/plano.md` — «O chat e o leitor»; «Interface». Requisitos: `REQ-CHT-007`, `REQ-CHT-008`, `REQ-LEI-011`, `REQ-A11`.

Animações **curtas** e nominais. Presença e hierarquia — não ruído. Duração típica na ordem das centenas de milissegundos (não segundos).

## Momentos obrigatórios

| Momento | Gatilho | Intenção |
| --- | --- | --- |
| **Mensagem** | Nova mensagem entra no fio | Entrada breve; o fio não salta de forma desorientadora |
| **Thumbs / miniaturas** | Miniaturas da resposta aparecem | Aparecimento curto (podem preceder a prosa) |
| **Leque** | Vários documentos; hover (rato) ou primeiro toque (tacto) | Abre o leque em miniatura |
| **Crescer até ao leitor** | Clique / segundo toque numa miniatura | A miniatura escolhida cresce até ao leitor |
| **Highlight uma vez** | Leitor abre numa citação / marca alvo | O highlight **acende uma vez** e fica estável |
| **Recolher** | Minimizar ou Escape no leitor | O leitor colapsa de volta à miniatura; chat no mesmo sítio |

## `prefers-reduced-motion: reduce`

- Encurtar ou saltar para o estado final quase imediato.
- **Não** remover o leque nem o leitor.
- Highlight: pode aparecer já no estado final sem pulso, desde que a marca fique visível.

## O que não animar

- Loop de highlight a piscar.
- Parallax ou glow contínuo no chrome.
- Animações longas que atrasem a leitura da prova.
- Motion decorativo em estados vazios.
