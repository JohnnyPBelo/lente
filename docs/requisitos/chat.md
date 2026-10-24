# Chat e leque — `REQ-CHT`

## REQ-CHT-001

**Enunciado:** A barra lateral em vidro lista conversas e permite criar nova, renomear e apagar.

**Origem:** docs/origem/plano.md — «O chat e o leitor»; «Interface»

**Critérios de aceitação:**

1. **Dado** a app aberta, **quando** o utilizador usa a barra lateral, **então** vê a lista de conversas e consegue criar uma conversa nova, renomear uma existente e apagar uma existente, com o resultado reflectido na lista.

**Não pede:** pastas aninhadas de conversas; sync de conversas para a nuvem.

---

## REQ-CHT-002

**Enunciado:** A primeira procura de uma conversa nova dá o nome à conversa.

**Origem:** docs/origem/plano.md — «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** uma conversa ainda sem nome definido pelo utilizador, **quando** o utilizador envia a primeira procura, **então** o título da conversa na barra lateral passa a derivar dessa procura (visivelmente actualizado).

**Não pede:** o utilizador a confirmar o título gerado; renomeação automática em todas as procuras seguintes.

---

## REQ-CHT-003

**Enunciado:** Quando há documentos no resultado, a mensagem mostra uma miniatura por documento, na página do primeiro highlight.

**Origem:** docs/origem/plano.md — «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** uma resposta com highlights em um ou mais documentos, **quando** a mensagem é mostrada, **então** cada documento envolvido tem uma miniatura correspondente à página do seu primeiro highlight.

**Não pede:** miniatura por cada highlight individual; re-render do PDF no hover (ver REQ-ING-011).

---

## REQ-CHT-004

**Enunciado:** Um documento: o clique na miniatura abre o leitor. Vários: o rato abre um leque ainda em miniatura; clicar numa abre o leitor (essa cresce até ao leitor).

**Origem:** docs/origem/plano.md — «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** exactamente um documento no resultado, **quando** o utilizador clica na miniatura, **então** o leitor abre nesse documento/highlight.
2. **Dado** vários documentos, **quando** o utilizador interage com o conjunto de miniaturas (hover/activação do leque), **então** aparece o leque em miniatura e, ao clicar numa, essa transição leva ao leitor nesse documento.

**Não pede:** abrir todos os documentos em separadores; leque fora da mensagem.

---

## REQ-CHT-005

**Enunciado:** Minimizar, ou Escape, recolhe o leitor até à miniatura e o chat continua no mesmo sítio.

**Origem:** docs/origem/plano.md — «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** o leitor aberto a partir de uma mensagem, **quando** o utilizador minimiza ou pressiona Escape, **então** o leitor recolhe para a miniatura e o scroll/posição do chat permanece no mesmo sítio observável.

**Não pede:** fechar a conversa; apagar a mensagem.

---

## REQ-CHT-006

**Enunciado:** Em tacto, o primeiro toque abre o leque e o segundo abre o documento.

**Origem:** docs/origem/plano.md — «O chat e o leitor»

**Critérios de aceitação:**

1. **Dado** vários documentos num dispositivo táctil, **quando** o utilizador toca uma vez no conjunto de miniaturas, **então** o leque abre; **quando** toca numa miniatura do leque, **então** o leitor abre nesse documento.

**Não pede:** gestos de pinça no leque; suporte a stylus específico.

---

## REQ-CHT-007

**Enunciado:** `prefers-reduced-motion` encurta o movimento sem tirar o leque nem o leitor.

**Origem:** docs/origem/plano.md — «O chat e o leitor»; ver também REQ-A11-001

**Critérios de aceitação:**

1. **Dado** o sistema com `prefers-reduced-motion: reduce`, **quando** o utilizador abre o leque e o leitor, **então** as animações são encurtadas ou reduzidas, mas leque e leitor continuam utilizáveis e presentes.

**Não pede:** desactivar por completo toda a UI motion fora deste media query; tema separado só para reduced motion.

---

## REQ-CHT-008

**Enunciado:** Animações curtas cobrem mensagem, miniaturas, leque, crescer até ao leitor, highlight a acender uma vez, e recolher. Interface em português; chrome em vidro líquido; Geist no chrome; serif no leitor.

**Origem:** docs/origem/plano.md — «O chat e o leitor»; «Interface»

**Critérios de aceitação:**

1. **Dado** uma resposta com documentos, **quando** a mensagem entra, as miniaturas aparecem, o leque abre, o leitor cresce, um highlight acende e o leitor recolhe, **então** cada um destes momentos tem animação curta observável (salvo reduced motion).
2. **Dado** a UI carregada, **quando** o utilizador lê chrome e leitor, **então** os textos de interface estão em português, o chrome usa o tratamento de vidro descrito no plano, e a superfície de leitura usa serif distinta do chrome (Geist).

**Não pede:** biblioteca de animação específica; dark/light toggle; i18n multi-língua.
