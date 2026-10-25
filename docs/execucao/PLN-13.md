# Ordem de trabalho PLN-13

Fonte: `docs/planos/PLN-13-chrome-da-interface.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Scaffold da UI em `apps/ui`: vidro líquido no chrome (fundo escuro neutro, blur, bordo de luz), Geist no chrome, layout com barra lateral de conversas e área de chat; PT; shadcn/ui reestilizado + motion curto; ainda sem barra de modos completa nem leitor.

## Fronteira

o que NÃO entra neste plano — leque/leitor (PLN-15), modos/lentes completos (PLN-14), dossier/alertas UI.

## Teste que falha primeiro, no plano

teste de componente/acessibilidade — `BarraLateral` renderiza botão «Nova conversa» e lista; com prop `conversas=[{id,nome}]` mostra o nome; contraste/rótulos em português (`Nova`, `Renomear`, `Apagar` via menu).

Nesta ordem esse teste é `reg-cht-001.test.tsx`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- Nenhuma. Pode partir de `main`.

## Ficheiros que este PR pode criar

- `apps/ui/package.json` — Node 22
- `apps/ui/src/main.tsx`
- `apps/ui/src/App.tsx`
- `apps/ui/src/styles/tokens.css` — variáveis de cor/vidro (evitar roxo default AI)
- `apps/ui/src/components/chrome/BarraLateral.tsx`
- `apps/ui/src/components/chrome/AreaChat.tsx`
- `apps/ui/src/components/chrome/CampoEscritaBase.tsx` — campo + botão `+` stub
- `apps/ui/src/lib/api.ts` — cliente `127.0.0.1:4317`
- `apps/ui/src/components/chrome/Mensagem.tsx`
- `tests` ou Playwright/vitest: `apps/ui/src/components/chrome/BarraLateral.test.tsx`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- apps/ui/src/components/barra/ (PLN-14)
- apps/ui/src/components/leque/, leitor/ e chat/CitacaoLink (PLN-15)
- engine/ excepto o cliente HTTP falso em apps/ui/src/lib/api.ts

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

Deixar em App.tsx sítios nomeados e vazios para a barra e para o leitor, sem os implementar. Copy de docs/interface/copy.md. Geist no chrome. Serif só no leitor, que é PLN-15. prefers-reduced-motion já se respeita na entrada da mensagem. O cliente fala só com 127.0.0.1.

## Requisitos que este PR fecha

- `REQ-CHT-001` fecha com `REG-CHT-001`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `apps/ui/src/components/chrome/reg-cht-001.test.tsx`
  - Dado a barra lateral, quando se cria, renomeia e apaga uma conversa, então a lista reflecte as três operações. Os rótulos visíveis são os de copy.md: Nova conversa, Renomear e Apagar.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] O texto visível vem de `docs/interface/copy.md`, sem frase inventada para o mesmo estado.

## Paralelo

Pode avançar já, com respostas falsas, ao lado do motor PLN-01 a PLN-12 e de PLN-16, PLN-19 e PLN-20. PLN-14 e PLN-15 esperam por este chrome.
