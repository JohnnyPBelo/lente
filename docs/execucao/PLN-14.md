# Ordem de trabalho PLN-14

Fonte: `docs/planos/PLN-14-barra-de-modos-e-lentes.md`. Este ramo não implementa a aplicação. A implementação entra depois, no mesmo pull request, quando as dependências estiverem fundidas e os caminhos de **Não tocar** forem respeitados.

## Objectivo

Barra de escrita única: menu `+` e `/` (setas, Enter, Escape); modos Procurar, Correlacionar, Confrontar, Alerta, Lacunas; pastilha de lente (investigar, assessment, acreditação, verificar); modo activo visível; sem páginas novas.

## Fronteira

o que NÃO entra neste plano — leque/leitor (PLN-15), implementação completa de alertas backend (PLN-19), export/import de correcções (fica no estado da aprendizagem na lateral, PLN-17).

## Teste que falha primeiro, no plano

`BarraEscrita.test.tsx` — pressionar `/` abre o menu; setas movem opção activa; Enter selecciona «Correlacionar» e a barra mostra dois campos «Conceito A» e «Conceito B»; Escape volta a Procurar de uma linha.

Nesta ordem esse teste é `reg-bar-004.test.tsx`. Se o caminho antigo do plano divergir do contrato já mergulhado em `main`, vale o contrato e o esquema, como está nas notas.

## Dependências

Têm de estar fundidos em `main` antes de se implementar:

- PLN-13

## Ficheiros que este PR pode criar

- `apps/ui/src/components/barra/BarraEscrita.tsx`
- `apps/ui/src/components/barra/MenuMais.tsx`
- `apps/ui/src/components/barra/PastilhaModo.tsx`
- `apps/ui/src/components/barra/PastilhaLente.tsx`
- `apps/ui/src/components/barra/modos/Procurar.tsx`
- `apps/ui/src/components/barra/modos/Correlacionar.tsx`
- `apps/ui/src/components/barra/modos/Confrontar.tsx`
- `apps/ui/src/components/barra/modos/Alerta.tsx`
- `apps/ui/src/components/barra/modos/Lacunas.tsx`
- `apps/ui/src/lib/lentes.ts` — mapeamento lente → prefixo/instrução
- `engine/api/rotas_modos.py` — correlacionar, confrontar, lacunas (mínimo)
- `tests` UI: `BarraEscrita.test.tsx`; API: `tests/api/test_modos.py`

Também os ficheiros de teste nomeados na secção de regressão, quando o plano ainda os não listava um a um.

## Não tocar

- apps/ui/src/components/chrome/ e App.tsx, donos de PLN-13: montar a barra no sítio que o chrome já deixou, sem reescrever a lateral
- apps/ui/src/components/leque/ e leitor/ (PLN-15)
- engine/api/rotas_chat.py (PLN-12). Este PR só cria rotas_modos.py
- engine/alertas/ (PLN-19) e engine/feedback/ de exportação (PLN-17)

- `docs/verificacao/cobertura.md`, que é do fecho
- `tests/regressao/test_suite.py`, `tests/regressao/apoio.py`, `tests/regressao/exigir_agora.py` e `scripts/regressao.sh`
- `docs/origem/plano.md`
- `data/`, `models/`, pesos `.gguf`, `.onnx`, `.safetensors`, `.pt`, `.pth`

Excepção partilhada: acrescentar linhas no fim de `tests/regressao/manifesto.txt`. Não apagar, não reordenar, não repetir.

## Notas para não reabrir o âmbito

Endpoints novos, em rotas_modos.py: HTTP-correlate, HTTP-confront e HTTP-lacunas, mais o que o contrato pede a estes modos. Não meter exportar nem importar correcções no menu. Strings de docs/interface/copy.md e docs/interface/barra.md. O limite de dez alertas no motor é REG-ALE-002.

## Requisitos que este PR fecha

- `REQ-BUS-009` fecha com `REG-BUS-009`.
- `REQ-BAR-001` fecha com `REG-BAR-001`.
- `REQ-BAR-002` fecha com `REG-BAR-002`.
- `REQ-BAR-003` fecha com `REG-BAR-003`.
- `REQ-BAR-004` fecha com `REG-BAR-004`.
- `REQ-BAR-005` fecha com `REG-BAR-005`.
- `REQ-BAR-006` fecha com `REG-BAR-006`.
- `REQ-BAR-007` fecha com `REG-BAR-007`.
- `REQ-BAR-008` fecha com `REG-BAR-008`.
- `REQ-BAR-009` fecha com `REG-BAR-009`.
- `REQ-BAR-010` fecha com `REG-BAR-010`.
- `REQ-BAR-011` fecha com `REG-BAR-011`.
- `REQ-A11-002` fecha com `REG-A11-002`.
- `REQ-SEG-006` fecha com `REG-SEG-006`.
- `REQ-FOR-010` fecha com `REG-FOR-010`.

## Testes de regressão

Acrescentar no fim de `tests/regressao/manifesto.txt`, e só no fim:

- `apps/ui/src/components/barra/reg-bus-009.test.tsx`
  - Dado uma procura normal, quando se vê o estado, então o limiar numérico em vigor está visível na interface e não só em logs.
- `apps/ui/src/components/barra/reg-bar-001.test.tsx`
  - Dado qualquer modo, quando se escreve ou envia, então a interacção fica na barra no fundo do chat e não navega para uma rota nova.
- `apps/ui/src/components/barra/reg-bar-002.test.tsx`
  - Dado a barra, quando se activa o botão +, então abre um menu curto em vidro por cima da barra com os modos.
- `apps/ui/src/components/barra/reg-bar-003.test.tsx`
  - Dado o foco na barra, quando se prime /, então abre o mesmo menu que o botão +.
- `apps/ui/src/components/barra/reg-bar-004.test.tsx`
  - Dado o menu aberto, quando as setas e Enter escolhem Correlacionar, então a barra mostra os campos Conceito A e Conceito B. Quando se prime Escape, então volta a Procurar de uma linha.
- `apps/ui/src/components/barra/reg-bar-005.test.tsx`
  - Dado um modo diferente de Procurar, quando se olha a barra, então a pastilha mostra o nome desse modo com a string de copy.md.
- `apps/ui/src/components/barra/reg-bar-006.test.tsx`
  - Dado o modo Procurar, quando a barra está em repouso, então há um campo de uma linha e Enter envia.
- `apps/ui/src/components/barra/reg-bar-007.test.tsx`
  - Dado Correlacionar, quando a barra se mostra, então os campos chamam-se Conceito A e Conceito B. Dado ambos preenchidos, quando se prime Enter, então os dois seguem no pedido. As três cores do resultado são REG-BUS-011.
- `apps/ui/src/components/barra/reg-bar-008.test.tsx`
  - Dado Confrontar, quando a barra se mostra, então há Trecho A e Trecho B com a acção Escolher. Sem citações, aceita texto colado. Dado A e B enviados, então a leitura é uma de Concordam, Contradizem-se ou Falam de assuntos diferentes, mais a pontuação, calculada só com as duas direcções do juiz e o cosseno. Clicar a citação abre o leitor no highlight.
- `apps/ui/src/components/barra/reg-bar-009.test.tsx`
  - Dado o modo Alerta, quando a barra se mostra, então há um único campo com o placeholder «O que queres que eu vigie?». Dado menos de dez alertas, quando se envia, então segue o pedido de criação. A recusa do décimo primeiro é REG-ALE-002; aqui só se mostra a copy alerts.limit se a API recusar.
- `apps/ui/src/components/barra/reg-bar-010.test.tsx`
  - Dado Lacunas, quando a barra se mostra, então é uma caixa de várias linhas: Shift+Enter parte a linha e Enter envia. O resultado é uma mensagem com Encontrado, Fraco ou Ausente por linha, e a rota não chama o escritor. A recusa no módulo do escritor é REG-RES-011.
- `apps/ui/src/components/barra/reg-bar-011.test.tsx`
  - Dado a barra, quando se escolhe uma lente, então a pastilha fica ao lado da do modo. Procurar, Alerta e Lacunas enviam essa lente. Confrontar mantém as três leituras. Os prefixos exactos do embedding são REG-BUS-002.
- `apps/ui/src/components/barra/reg-a11-002.test.tsx`
  - Dado o foco na barra e só o teclado, quando se usa + ou /, setas, Enter e Escape, então dá para abrir o menu, escolher um modo, confirmá-lo e voltar a Procurar sem rato, com nome acessível nos controlos.
- `apps/ui/src/components/barra/reg-seg-006.test.tsx`
  - Dado a copy e os identificadores de modo deste PR, quando se procuram fluxos, então nenhum se declara como playbook ofensivo nem como geração de procedimentos de ataque.
- `apps/ui/src/components/barra/reg-for-010.test.tsx`
  - Dado os modos e as lentes implementados, quando se listam, então são só Procurar, Correlacionar, Confrontar, Alerta e Lacunas, e as lentes Investigar, Assessment, Acreditação e Verificar. Não há entrada para gerar procedimentos de ataque.

Um teste de UI é o caminho do ficheiro `.test.tsx`, que já contém o `reg` no nome. Um teste de motor é o node id `caminho::test_reg_…`.

## Definição de pronto

- [ ] O comportamento acima está implementado dentro da fronteira.
- [ ] `scripts/regressao.sh` está verde.
- [ ] O manifesto cresceu exactamente com os identificadores desta ordem.
- [ ] Não há ficheiros de pesos no git.
- [ ] O texto visível vem de `docs/interface/copy.md`, sem frase inventada para o mesmo estado.

## Paralelo

Pode avançar ao lado de PLN-15 se não editar leque, leitor, citações nem rotas_documento.py, e se não reescrever App.tsx. Pode avançar ao lado de PLN-16, PLN-19 e do motor de PLN-20.
