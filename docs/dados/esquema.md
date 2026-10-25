# Esquema SQLite — Lente

Esquema lógico do ficheiro em `data/` (nome concreto da app a definir na implementação). Tipos SQLite habituais: `INTEGER`, `TEXT`, `REAL`, `BLOB`. Datas em ISO-8601 UTC (`TEXT`). Booleanos como `INTEGER` 0/1. Identificadores surrogados `INTEGER PRIMARY KEY` (rowid) salvo indicação em contrário.

Convenções:

- `…_em` — instante de criação ou atualização.
- Chaves estrangeiras com `ON DELETE CASCADE` ou `RESTRICT` conforme a nota de cada tabela.
- Índices listados após cada tabela; nomes sugeridos `idx_<tabela>_<colunas>`.

---

## Visão geral

```text
documentos ──< documento_hashes
     │
     ├──< blocos ──< frases
     │       │         │
     │       └── vectores (sqlite-vec) / FTS5
     │
     ├──< documento_etiquetas >── etiquetas
     └──  fila (um documento em curso)

conversas ──< mensagens ──< citacoes
                 │
                 └──< trechos_fixados

feedback (pares juiz)
dossiers (fotografia JSON + metadados)
alertas
diario (append-only)
versoes_modelo
```

---

## `documentos`

Biblioteca local. Um registo por caminho conhecido; o SHA-256 actual e o estado de frescura evitam responder com índice velho em silêncio.

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `caminho` | `TEXT` | Caminho absoluto ou canónico no disco; `UNIQUE` |
| `titulo` | `TEXT` | Título mostrado; pode vir do ficheiro ou do utilizador |
| `tipo` | `TEXT` | Tipo escolhido/manual (filtro da biblioteca) |
| `tipo_sugerido` | `TEXT` | Sugestão por embedding; só sugestão, não substitui `tipo` |
| `sha256` | `TEXT` | Hex do conteúdo actual em disco (ou último conhecido na ingestão) |
| `estado` | `TEXT` | `ok` \| `desactualizado` \| `a_indexar` \| `erro` |
| `paginas` | `INTEGER` | Número de páginas quando aplicável; `NULL` se desconhecido |
| `miniatura_caminho` | `TEXT` | Caminho da miniatura gerada na indexação; `NULL` se ainda não há |
| `sumario_json` | `TEXT` | JSON dos títulos extraídos para o sumário do leitor; `NULL` até indexar |
| `criado_em` | `TEXT` | |
| `actualizado_em` | `TEXT` | |
| `indexado_em` | `TEXT` | Última indexação bem-sucedida; `NULL` se nunca |

**Restrições:** `CHECK (estado IN ('ok', 'desactualizado', 'a_indexar', 'erro'))`.

**Índices:**

- `UNIQUE (caminho)`
- `idx_documentos_estado` em `(estado)`
- `idx_documentos_tipo` em `(tipo)`
- `idx_documentos_sha256` em `(sha256)`

**Notas:** Se o ficheiro em disco mudar de hash, a biblioteca marca `estado = 'desactualizado'` em vez de servir blocos antigos. Reindexação volta a `ok` e actualiza `sha256` / `indexado_em`.

---

## `documento_hashes`

Histórico de versões por conteúdo. Permite saber que SHA-256 estava indexado e ligar dossiers/citações a uma geração concreta do ficheiro.

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `documento_id` | `INTEGER` | FK → `documentos(id)` `ON DELETE CASCADE` |
| `sha256` | `TEXT` | Hex dos bytes nessa versão |
| `visto_em` | `TEXT` | Quando esta versão foi observada / indexada |
| `activa` | `INTEGER` | 1 se é a versão cujo índice está em vigor; 0 histórico |

**Restrições:** `UNIQUE (documento_id, sha256)`.

**Índices:**

- `idx_documento_hashes_doc` em `(documento_id, activa)`
- `idx_documento_hashes_sha` em `(sha256)`

**Notas:** Ao reindexar, a linha activa anterior passa a `activa = 0`; a nova versão fica `activa = 1`. Dossiers guardam o SHA-256 no fecho (ver `dossiers`) e comparam com o ficheiro actual ao reabrir.

---

## `blocos`

Unidades de indexação semântica. Alvo: cerca de **500 tokens**, com **sobreposição de 50** tokens entre blocos consecutivos do mesmo documento/versão.

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `documento_id` | `INTEGER` | FK → `documentos(id)` `ON DELETE CASCADE` |
| `hash_id` | `INTEGER` | FK → `documento_hashes(id)` `ON DELETE CASCADE`; versão indexada |
| `ordem` | `INTEGER` | Ordem no documento (0-based) |
| `texto` | `TEXT` | Texto do bloco |
| `pagina_inicio` | `INTEGER` | Primeira página coberta (1-based); `NULL` se não aplicável |
| `pagina_fim` | `INTEGER` | Última página coberta; `NULL` se não aplicável |
| `offset_inicio` | `INTEGER` | Offset de carácter no texto extraído do documento |
| `offset_fim` | `INTEGER` | Exclusive ou inclusive — a implementação fixa uma convenção e documenta-a |
| `tokens_aprox` | `INTEGER` | Contagem aproximada usada no corte |

**Restrições:** `UNIQUE (hash_id, ordem)`.

**Índices:**

- `idx_blocos_documento` em `(documento_id)`
- `idx_blocos_hash_ordem` em `(hash_id, ordem)`

---

## `frases`

Frases (ou unidades de highlight) dentro de um bloco. O juiz e o leitor trabalham ao nível da frase: offsets e caixas para pintar o intervalo literal.

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `bloco_id` | `INTEGER` | FK → `blocos(id)` `ON DELETE CASCADE` |
| `documento_id` | `INTEGER` | FK → `documentos(id)` `ON DELETE CASCADE` (desnormalizado para consultas) |
| `pagina` | `INTEGER` | Página principal do highlight; `NULL` se não aplicável |
| `texto` | `TEXT` | Texto literal da frase |
| `offset_inicio` | `INTEGER` | No texto do documento (ou do bloco — convenção única na implementação) |
| `offset_fim` | `INTEGER` | |
| `caixas_json` | `TEXT` | JSON array de caixas `{ "pagina", "x", "y", "largura", "altura" }` (coordenadas do PDF/imagem) |
| `ordem` | `INTEGER` | Ordem dentro do bloco |

**Índices:**

- `idx_frases_bloco` em `(bloco_id, ordem)`
- `idx_frases_documento_pagina` em `(documento_id, pagina)`

**Notas:** Cada marca no leitor é um intervalo literal; `caixas_json` permite highlight em PDF com layout. Texto colado / Markdown pode ter `caixas_json` vazio `[]`.

---

## Vectores (`sqlite-vec`) — 256 dimensões

EmbeddingGemma 2: vector de **256** dimensões (corte Matryoshka do de 768), **normalizado**, float32. Pesquisa por **cosseno exacto** (varrimento), não índice aproximado.

A extensão oficial cria uma tabela virtual; a forma exacta depende da versão de `sqlite-vec` ligada. Modelo lógico:

### Opção A — tabela virtual por bloco

```sql
-- Ilustrativo; sintaxe conforme a versão de sqlite-vec adoptada.
CREATE VIRTUAL TABLE vectores_blocos USING vec0(
  bloco_id INTEGER PRIMARY KEY,
  embedding float[256]
);
```

### Opção B — tabela auxiliar + virtual

| Coluna (auxiliar `vectores`) | Tipo | Notas |
| --- | --- | --- |
| `bloco_id` | `INTEGER` | PK, FK → `blocos(id)` `ON DELETE CASCADE` |
| `hash_id` | `INTEGER` | FK → `documento_hashes(id)` |
| `dimensoes` | `INTEGER` | Sempre 256 nesta versão do produto |
| `embedding` | `BLOB` | float32 little-endian, 256 × 4 bytes, **L2-normalizado** |

A tabela virtual `sqlite-vec` indexa o mesmo conteúdo para `MATCH` / distância de cosseno no SQL.

**Consultas (conceito):**

```sql
-- Cosseno exacto: com vectores normalizados, distância = 1 - produto interno
-- (API exacta: função/operador da extensão carregada.)
SELECT bloco_id, distancia
FROM vectores_blocos
WHERE embedding MATCH ?
ORDER BY distancia
LIMIT ?;
```

**Notas de integração:**

1. Carregar a extensão no mesmo processo Python/UI que abre o SQLite (`sqlite3.enable_load_extension` / equivalente).
2. Não usar a extensão Vec1 oficial do SQLite (índice aproximado, pré-1.0) — o plano exige cosseno exacto.
3. Não entram Qdrant, Chroma, LanceDB nem Postgres.
4. Prefixos de embedding (documento / query) vivem no código de indexação e pesquisa, não em colunas extra.
5. Ao apagar ou reindexar um `hash_id`, remover os vectores dessa geração antes de inserir os novos.

**Índices:** a PK em `bloco_id` basta para junção; a pesquisa k-NN é da virtual table.

---

## FTS5 — texto de blocos e frases

Tabela virtual FTS5 sobre o texto pesquisável (termo exacto: cláusula, CVE, sigla).

```sql
CREATE VIRTUAL TABLE fts_texto USING fts5(
  texto,
  origem UNINDEXED,      -- 'bloco' | 'frase'
  origem_id UNINDEXED,   -- id em blocos ou frases
  documento_id UNINDEXED,
  hash_id UNINDEXED,
  tokenize = 'unicode61'
);
```

| Coluna FTS | Papel |
| --- | --- |
| `texto` | Conteúdo indexado |
| `origem` | Distingue bloco vs frase |
| `origem_id` | PK da linha de origem |
| `documento_id` / `hash_id` | Filtros pós-MATCH no código |

**Manutenção:** triggers ou lógica de ingestão mantêm FTS alinhado com `blocos` / `frases`. Na reindexação, apagar linhas FTS do `hash_id` antigo e reinserir.

**Fusão:** candidatos FTS5 + candidatos embedding → fusão por rank recíproco no código → juiz filtra o que se marca.

---

## `conversas`

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `titulo` | `TEXT` | Primeira procura dá o nome; renomeável |
| `criado_em` | `TEXT` | |
| `actualizado_em` | `TEXT` | Actualizado a cada mensagem |
| `apagada` | `INTEGER` | Soft-delete opcional; 0 por omissão |

**Índices:** `idx_conversas_actualizado` em `(actualizado_em DESC)`.

---

## `mensagens`

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `conversa_id` | `INTEGER` | FK → `conversas(id)` `ON DELETE CASCADE` |
| `papel` | `TEXT` | `utilizador` \| `assistente` \| `sistema` |
| `modo` | `TEXT` | `procurar` \| `correlacionar` \| `confrontar` \| `alerta` \| `lacunas` \| `NULL` |
| `lente` | `TEXT` | `investigar` \| `assessment` \| `acreditacao` \| `verificar` \| `NULL` |
| `conteudo` | `TEXT` | Prosa ou payload estruturado (ex. lacunas) em texto/JSON |
| `meta_json` | `TEXT` | Metadados do turno (conceitos A/B, leitura do confronto, etc.) |
| `criado_em` | `TEXT` | |

**Restrições:** `CHECK` nos conjuntos de `papel` / `modo` / `lente` aceites.

**Índices:** `idx_mensagens_conversa` em `(conversa_id, id)`.

---

## `citacoes`

Frases/trechos ligados a uma mensagem de assistente (highlights que passaram as portas).

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `mensagem_id` | `INTEGER` | FK → `mensagens(id)` `ON DELETE CASCADE` |
| `documento_id` | `INTEGER` | FK → `documentos(id)` `ON DELETE RESTRICT` |
| `frase_id` | `INTEGER` | FK → `frases(id)` `ON DELETE SET NULL`; `NULL` se a frase já não existe |
| `indice` | `INTEGER` | Número `[n]` na prosa |
| `trecho_literal` | `TEXT` | Cópia do texto no momento da resposta |
| `ficheiro` | `TEXT` | Caminho ou nome mostrado |
| `pagina` | `INTEGER` | |
| `offset_inicio` | `INTEGER` | |
| `offset_fim` | `INTEGER` | |
| `caixas_json` | `TEXT` | |
| `pontuacao_juiz` | `REAL` | Score do juiz nesse highlight |
| `sha256_ficheiro` | `TEXT` | Hash dos bytes no momento da citação (opcional se redunda com dossier) |

**Índices:** `idx_citacoes_mensagem` em `(mensagem_id, indice)`.

---

## `trechos_fixados`

Linha no SQLite para reabrir o chat sem nova procura (gesto «fixar» no leitor).

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `mensagem_id` | `INTEGER` | FK → `mensagens(id)` `ON DELETE CASCADE` |
| `conversa_id` | `INTEGER` | FK → `conversas(id)` `ON DELETE CASCADE` |
| `documento_id` | `INTEGER` | FK → `documentos(id)` `ON DELETE RESTRICT` |
| `frase_id` | `INTEGER` | FK → `frases(id)` `ON DELETE SET NULL` |
| `trecho_literal` | `TEXT` | |
| `ficheiro` | `TEXT` | |
| `pagina` | `INTEGER` | |
| `offset_inicio` | `INTEGER` | |
| `offset_fim` | `INTEGER` | |
| `caixas_json` | `TEXT` | |
| `fixado_em` | `TEXT` | |

**Índices:** `idx_trechos_fixados_mensagem` em `(mensagem_id)`; `idx_trechos_fixados_conversa` em `(conversa_id)`.

---

## `feedback`

Pares para o juiz (positivos / negativos). «Descartar» não cria linha. Base do LoRA e do export de correções.

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `mensagem_id` | `INTEGER` | FK → `mensagens(id)` `ON DELETE SET NULL` |
| `pergunta` | `TEXT` | Pergunta (ou reformulação) associada |
| `trecho` | `TEXT` | Texto do trecho |
| `etiqueta` | `TEXT` | `positivo` \| `negativo` |
| `lente` | `TEXT` | Lente activa no momento |
| `hash_par` | `TEXT` | Hash estável do par (pergunta+trecho+etiqueta+…); deduplicação na importação |
| `documento_id` | `INTEGER` | FK opcional |
| `frase_id` | `INTEGER` | FK opcional |
| `origem` | `TEXT` | `local` \| `importado` |
| `criado_em` | `TEXT` | |

**Restrições:** `CHECK (etiqueta IN ('positivo', 'negativo'))`; `UNIQUE (hash_par)` (pares repetidos entram uma vez).

**Índices:** `idx_feedback_lente` em `(lente)`; `idx_feedback_criado` em `(criado_em)`.

**Notas:** «Acertou» marca trechos mostrados como positivos; «Corrigir» marca as marcas da resposta como negativas e a selecção como positiva. Não altera o E2B.

---

## `dossiers`

Fotografia congelada ao fechar. Reabrir lê estes campos; não volta a correr modelos. Export Markdown + JSON usam o mesmo conteúdo.

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `conversa_id` | `INTEGER` | FK → `conversas(id)` `ON DELETE RESTRICT` |
| `titulo` | `TEXT` | |
| `fechado_em` | `TEXT` | Data/hora do fecho |
| `perguntas_json` | `TEXT` | Lista de perguntas do ecrã |
| `frases_json` | `TEXT` | Frases aceites: trecho literal, ficheiro, página, offsets, caixas, pontuação do juiz |
| `ficheiros_json` | `TEXT` | Por ficheiro citado: caminho, `sha256` dos bytes no fecho |
| `versao_embedding` | `TEXT` | Id/versão EmbeddingGemma usada |
| `versao_juiz` | `TEXT` | Id do juiz ONNX (+ LoRA se houver) |
| `versao_e2b` | `TEXT` | Id/versão Gemma 4 E2B |
| `export_json` | `TEXT` | Cópia canónica alinhada a [dossier.schema.json](dossier.schema.json); opcional se se regenera a partir das colunas |

**Índices:** `idx_dossiers_conversa` em `(conversa_id)`; `idx_dossiers_fechado` em `(fechado_em DESC)`.

**Campos obrigatórios na fotografia (plano):**

- perguntas e frases que ficaram no ecrã
- por frase: trecho literal, ficheiro, página, offsets, caixas, pontuação do juiz
- SHA-256 dos bytes de cada ficheiro nesse momento
- data; versões EmbeddingGemma, juiz (incl. LoRA) e E2B

Se ao reabrir o hash em disco diferir, a UI indica que a fonte mudou; a prova antiga mantém-se.

---

## `alertas`

Máximo **10** alertas. Cada um tem fio próprio; documentos novos indexados passam pelo juiz só nessas frases.

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `consulta` | `TEXT` | Texto «O que queres que eu vigie?» |
| `lente` | `TEXT` | Lente de trabalho |
| `activo` | `INTEGER` | 1 ligado, 0 desligado (interruptor no topo do fio) |
| `conversa_id` | `INTEGER` | FK → `conversas(id)`; fio do alerta |
| `criado_em` | `TEXT` | |
| `actualizado_em` | `TEXT` | |

**Restrições:** na aplicação, recusar criar se `COUNT(*) WHERE activo IS NOT NULL` (ou total de alertas) ≥ 10 — o plano fixa teto de dez no total.

**Índices:** `idx_alertas_activo` em `(activo)`.

---

## `diario`

Append-only: sem `UPDATE` de conteúdo histórico (excepto retenção futura fora de âmbito actual).

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `tipo` | `TEXT` | `procura` \| `abertura` \| `feedback` \| `fecho_dossier` |
| `payload_json` | `TEXT` | Detalhe do evento |
| `criado_em` | `TEXT` | |

**Índices:** `idx_diario_tipo_em` em `(tipo, criado_em)`; `idx_diario_criado` em `(criado_em)`.

**Notas:** Sem contas nem rede. Tipos cobrem procuras, documentos abertos, feedback e fechos de dossier.

---

## `etiquetas`

Etiquetas manuais do utilizador para filtrar a biblioteca.

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `nome` | `TEXT` | `UNIQUE`, normalizado na UI |
| `criado_em` | `TEXT` | |

---

## `documento_etiquetas`

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `documento_id` | `INTEGER` | FK → `documentos(id)` `ON DELETE CASCADE` |
| `etiqueta_id` | `INTEGER` | FK → `etiquetas(id)` `ON DELETE CASCADE` |

**PK composta:** `(documento_id, etiqueta_id)`.

**Índices:** `idx_documento_etiquetas_etiqueta` em `(etiqueta_id)`.

---

## `versoes_modelo`

Registo das versões em uso (embedding, juiz+LoRA, E2B) para dossiers, diagnóstico e compatibilidade de importação de correções.

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `papel` | `TEXT` | `embedding` \| `juiz` \| `e2b` |
| `modelo_id` | `TEXT` | Identificador Hugging Face / ficheiro ONNX / etc. |
| `revisao` | `TEXT` | Hash, tag ou caminho de artefacto |
| `lora_id` | `TEXT` | Só juiz: id do adaptador activo; `NULL` se só base ONNX |
| `activo` | `INTEGER` | 1 se é a versão corrente desse papel |
| `notas` | `TEXT` | |
| `registado_em` | `TEXT` | |

**Índices:** `UNIQUE (papel, modelo_id, revisao, IFNULL(lora_id, ''))` ou equivalente; `idx_versoes_activo` em `(papel, activo)`.

---

## `fila`

Fila de ingestão: **um documento de cada vez** (trabalho pesado único; procura pausa indexação).

| Coluna | Tipo | Notas |
| --- | --- | --- |
| `id` | `INTEGER` | PK |
| `documento_id` | `INTEGER` | FK → `documentos(id)` `ON DELETE CASCADE` |
| `estado` | `TEXT` | `pendente` \| `em_curso` \| `concluido` \| `erro` |
| `prioridade` | `INTEGER` | Menor = mais cedo; omissão 100 |
| `erro_mensagem` | `TEXT` | `NULL` se sem erro |
| `criado_em` | `TEXT` | |
| `iniciado_em` | `TEXT` | |
| `concluido_em` | `TEXT` | |

**Restrições de aplicação:** no máximo uma linha `em_curso` em qualquer instante.

**Índices:** `idx_fila_estado_prio` em `(estado, prioridade, id)`.

---

## Integridade e PRAGMA

Recomendações de abertura:

```sql
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
```

Backup: zip da pasta `data/` (ficheiro SQLite + miniaturas + artefactos locais), sem nuvem.

---

## Mapa plano → tabelas

| Ideia no plano | Tabelas / objectos |
| --- | --- |
| SHA-256 e desactualizado | `documentos`, `documento_hashes` |
| Blocos ~500 / overlap 50 | `blocos` |
| Frases, offsets, caixas | `frases` |
| Vectores 256-d, cosseno exacto | virtual `sqlite-vec` (+ auxiliar) |
| FTS5 | `fts_texto` |
| Chat, citações, fixar | `conversas`, `mensagens`, `citacoes`, `trechos_fixados` |
| Feedback juiz / LoRA | `feedback`, `versoes_modelo` |
| Dossier congelado | `dossiers` |
| Alertas ≤ 10 | `alertas` |
| Diário append-only | `diario` |
| Etiquetas manuais | `etiquetas`, `documento_etiquetas` |
| Fila de um documento | `fila` |
