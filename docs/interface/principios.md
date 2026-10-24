# Princípios de interface

Origem: `docs/origem/plano.md` — «Interface»; «O chat e o leitor».

## Idioma

Toda a UI é **português de Portugal**: rótulos, placeholders, avisos, feedback, estados vazios, menus e exportações. Sem strings em inglês na superfície do produto. Ver [copy.md](copy.md).

## Duas superfícies

| Zona | Tratamento | Tipografia |
| --- | --- | --- |
| **Chrome** (barra lateral, barra de escrita, menus, pastilhas, chrome do leitor, leque) | Vidro líquido | Geist |
| **Texto do leitor** (corpo do documento) | Superfície sólida | Serif |

O chrome nunca invade a tipografia do corpo: o documento lê-se em serif sobre fundo opaco. O chat e os controlos ficam no vidro.

## Vidro líquido (chrome)

- Fundo **escuro neutro** (sem violeta de default, sem glow ornamental).
- **Blur** atrás do painel (backdrop-filter).
- **Bordo de luz** fino (highlight de 1 px, baixa opacidade).
- Transparência moderada: o conteúdo atrás adivinha-se sem competir com o texto do chrome.
- Menus curtos (ex.: `+` / `/`) abrem **por cima da barra**, no mesmo idioma visual.

Não é tema claro/escuro configurável nesta especificação. Não é glassmorphism decorativo em cartões de conteúdo.

## Superfície do leitor

- Fundo **sólido** (opaco), contraste estável para leitura longa.
- Tipografia **serif** no corpo; títulos do documento seguem a hierarquia extraída, ainda em serif.
- Chrome do leitor (páginas, zoom, sumário, bolha Confrontar) mantém-se em vidro + Geist.

## Componentes e motion

- Base: **shadcn/ui**, **reestilizado** para o vidro e a paleta neutra — não o look default (roxo/indigo, pills arredondadas em excesso, multi-shadow).
- **Motion** curto e intencional: ver [movimento.md](movimento.md). `prefers-reduced-motion: reduce` encurta sem remover leque nem leitor.
- Tokens CSS próprios (fundo, blur, bordo, pastilha, destaque de highlight); Geist no chrome; serif no leitor.

## Composição

- Um sítio para escrever: a barra no fundo do chat. Sem páginas novas por modo.
- Prova na página: citação → leitor com highlight. O leque é escolha manual quando há vários documentos.
- Feedback discreto na mensagem (`Acertou` / `Corrigir` / `Descartar`); não bloqueia a procura seguinte.
- Exportar/Importar correções vive no **estado de aprendizagem** no topo da barra lateral — não no menu `+`.

## Fora desta superfície

Contas, sync, tema multi-idioma, Electron, segundo modo «só GPU». A UI corre no browser local; o motor Python serve a app construída.
