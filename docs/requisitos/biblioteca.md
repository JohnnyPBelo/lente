# Biblioteca — `REQ-BIB`

## REQ-BIB-001

**Enunciado:** O utilizador pode pôr etiquetas nos documentos para filtrar a biblioteca.

**Origem:** docs/origem/plano.md — «Mais, ainda sem peso»

**Critérios de aceitação:**

1. **Dado** um documento na biblioteca, **quando** o utilizador lhe atribui uma ou mais etiquetas, **então** essas etiquetas ficam persistidas.
2. **Dado** etiquetas existentes, **quando** o utilizador filtra a biblioteca por etiqueta, **então** só aparecem os documentos com essa etiqueta.

**Não pede:** taxonomia hierárquica obrigatória; etiquetas geradas automaticamente como verdade (só sugestão de tipo — REQ-BIB-002).

---

## REQ-BIB-002

**Enunciado:** O tipo de documento é um filtro manual; a sugestão de tipo por embedding que já existe continua a ser só uma sugestão.

**Origem:** docs/origem/plano.md — «Mais, ainda sem peso»; «Pesquisa, sem modelo a mais»

**Critérios de aceitação:**

1. **Dado** a biblioteca, **quando** o utilizador filtra por tipo, **então** o filtro aplicado é a escolha manual do utilizador.
2. **Dado** uma sugestão de tipo por semelhança de embedding, **quando** o utilizador não a confirma, **então** essa sugestão não substitui o tipo/filtro manual como facto.

**Não pede:** classificador separado treinado; obrigar o utilizador a aceitar a sugestão.

---

## REQ-BIB-003

**Enunciado:** A lista da biblioteca é virtualizada, para milhares de ficheiros não pesarem na interface.

**Origem:** docs/origem/plano.md — «Pesquisa, sem modelo a mais»

**Critérios de aceitação:**

1. **Dado** uma biblioteca com milhares de documentos, **quando** o utilizador abre e faz scroll na lista, **então** a UI permanece responsiva mediante virtualização (não monta todos os nós DOM dos milhares de linhas de uma vez).

**Não pede:** paginação servidor remota; pesquisa full-text na lista sem FTS5/embedding.
