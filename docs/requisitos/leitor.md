# Leitor — `REQ-LEI`

## REQ-LEI-001

**Enunciado:** O leitor abre o documento inteiro: PDF, texto, Markdown, página de URL ou imagem.

**Origem:** docs/origem/plano.md — «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** um documento de cada tipo suportado (PDF, texto, Markdown, página de URL, imagem) indexado, **quando** o utilizador o abre no leitor, **então** o conteúdo completo desse documento é navegável no leitor (não só o excerto da citação).

**Não pede:** edição in-place do ficheiro; suporte a formatos binários de escritório além do fluxo de ingestão (`.docx` via extracção).

---

## REQ-LEI-002

**Enunciado:** Scroll contínuo, highlights em todas as páginas atingidas, salto entre marcas.

**Origem:** docs/origem/plano.md — «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** um documento multi-página com vários highlights, **quando** o leitor está aberto, **então** o scroll é contínuo, os highlights estão visíveis em todas as páginas atingidas, e existe acção para saltar entre marcas.

**Não pede:** modo página-a-página exclusivo sem scroll contínuo; edição das marcas no sentido de alterar o ficheiro fonte.

---

## REQ-LEI-003

**Enunciado:** Zoom; arrastar numa imagem ou num scan; ajustar à largura e à página.

**Origem:** docs/origem/plano.md — «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** o leitor aberto, **quando** o utilizador usa zoom e «ajustar à largura» / «ajustar à página», **então** a vista reflecte essas escalas.
2. **Dado** uma imagem ou página de scan, **quando** o utilizador arrasta, **então** a vista pan/move o conteúdo conforme o zoom.

**Não pede:** anotações desenhadas livres; rotação arbitrária persistida.

---

## REQ-LEI-004

**Enunciado:** Controlo de páginas, ir para uma página, e procurar neste documento.

**Origem:** docs/origem/plano.md — «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** um documento paginado, **quando** o utilizador indica um número de página, **então** o leitor navega para essa página.
2. **Dado** texto no documento, **quando** o utilizador usa «procurar neste documento» com um termo presente, **então** encontra ocorrências dentro do documento aberto.

**Não pede:** pesquisa neste documento a usar o EmbeddingGemma; regex avançada.

---

## REQ-LEI-005

**Enunciado:** Sumário com os títulos extraídos na indexação.

**Origem:** docs/origem/plano.md — «O chat e o leitor»; REQ-ING-010

**Critérios de aceitação:**

1. **Dado** um documento cujos títulos foram extraídos na indexação, **quando** o utilizador abre o sumário no leitor, **então** vê essa lista e pode navegar para a secção correspondente.

**Não pede:** sumário gerado por LLM se a extracção na indexação falhou; edição do sumário pelo utilizador.

---

## REQ-LEI-006

**Enunciado:** Seleccionar, copiar, e copiar a citação já com ficheiro e página.

**Origem:** docs/origem/plano.md — «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** texto no leitor, **quando** o utilizador selecciona e copia, **então** o texto seleccionado fica na área de transferência.
2. **Dado** uma selecção ou highlight, **quando** o utilizador escolhe copiar a citação, **então** a cópia inclui identificação de ficheiro e página.

**Não pede:** formato de citação académica (APA/ISO) configurável; partilha para redes.

---

## REQ-LEI-007

**Enunciado:** A selecção serve para corrigir o highlight (fluxo Corrigir do feedback).

**Origem:** docs/origem/plano.md — «O chat e o leitor»; «Feedback, só no juiz»

**Critérios de aceitação:**

1. **Dado** o fluxo Corrigir activo, **quando** o utilizador selecciona texto no leitor, **então** essa selecção fica registada como trecho positivo e as marcas da resposta em correcção ficam negativas (REQ-FBK-005).

**Não pede:** correcção sem passar pelo feedback Acertou/Corrigir/Descartar; treino imediato PyTorch a cada selecção.

---

## REQ-LEI-008

**Enunciado:** Fixar um trecho na mensagem grava uma linha no SQLite, para o encontrar ao reabrir o chat sem nova procura.

**Origem:** docs/origem/plano.md — «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** texto seleccionado ou um highlight no leitor ligado a uma mensagem, **quando** o utilizador fixa o trecho, **então** existe um registo persistente no SQLite.
2. **Dado** a app reiniciada e o mesmo chat reaberto, **quando** o utilizador vê a mensagem, **então** o trecho fixado continua acessível sem nova procura.

**Não pede:** sincronizar trechos fixados entre máquinas; limite ilimitado sem política de armazenamento.

---

## REQ-LEI-009

**Enunciado:** Superfície do texto sólida, com serif. O chrome do leitor segue em vidro.

**Origem:** docs/origem/plano.md — «O chat e o leitor»; «Interface»

**Critérios de aceitação:**

1. **Dado** o leitor aberto, **quando** se observa a área de leitura vs. chrome, **então** o texto assenta numa superfície sólida com tipografia serif, distinta do chrome em vidro.

**Não pede:** escolha livre de tipografia pelo utilizador; modo contraste WCAG AAA documentado neste requisito (ver REQ-A11).

---

## REQ-LEI-010

**Enunciado:** No leitor, com texto seleccionado, uma bolha «Confrontar» enche o primeiro lugar vazio do modo Confrontar e traz o utilizador de volta à barra para escolher o segundo.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** texto seleccionado no leitor, **quando** o utilizador activa a bolha «Confrontar», **então** o modo Confrontar fica activo, o primeiro lugar vazio (A ou B) fica preenchido com essa selecção/ficheiro/página, e o foco volta à barra para o segundo lugar.

**Não pede:** preencher automaticamente os dois lugares com a mesma selecção; confronto sem juiz.

---

## REQ-LEI-011

**Enunciado:** O highlight acende uma vez ao chegar; minimizar/Escape recolhe até à miniatura mantendo o chat (alinhado a REQ-CHT-005).

**Origem:** docs/origem/plano.md — «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** abertura do leitor a partir de uma citação, **quando** a página alvo carrega, **então** o highlight correspondente acende uma vez (animação curta, salvo reduced motion).
2. **Dado** o leitor aberto, **quando** o utilizador minimiza ou Escape, **então** regressa à miniatura no chat no mesmo sítio.

**Não pede:** highlight a piscar em loop; histórico de highlights visitados na sessão.
