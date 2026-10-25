# Contrato HTTP

Todos os endpoints: **só** `http://127.0.0.1:4317`. Sem TLS, sem autenticação, sem escuta noutro endereço por omissão. Exemplos JSON sintéticos.

IDs `HTTP-…` conforme [docs/LEITURA.md](../LEITURA.md).

## Convenções

| Campo | Regra |
| --- | --- |
| Content-Type | `application/json` salvo download binário (`application/zip`, `text/markdown`) |
| Erros | `{ "erro": "codigo", "mensagem": "texto observável" }` |
| IDs | strings opacas (`cht_…`, `doc_…`, `dos_…`, `ale_…`) |
| Lentes | `investigar` \| `assessment` \| `acreditacao` \| `verificar` (além do modo da barra) |
| Stream | `text/event-stream` onde indicado; eventos `data: {…}\n\n` |

### Streaming de prosa (duas portas)

Em procura e correlacionar, a prosa **só** entra no fio depois de passar:

1. a frase termina com `[n]` de um trecho do pacote desta procura;
2. o juiz confirma fidelidade frase↔trecho.

Ordem típica no stream:

1. `miniaturas` — podem chegar primeiro;
2. `excerto` — trechos/highlights candidatos;
3. `frase` — **só** frases aceites (nunca provisórias a apagar);
4. `vazio` — se nenhuma frase sobreviver (excertos/miniaturas podem já ter saído);
5. `fim`.

Alertas e lacunas **não** abrem stream de prosa do E2B.

---

## Saúde

### HTTP-health

`GET /health`

**Resposta 200**

```json
{
  "ok": true,
  "versao": "0.0.0",
  "modelos": {
    "embedding": "pronto",
    "juiz": "pronto",
    "escritor": "ausente"
  },
  "disco_data_mb": 128
}
```

---

## Pesquisa e modos da barra

### HTTP-search

`POST /search`

**Pedido**

```json
{
  "chat_id": "cht_01",
  "texto": "Quem aprova o acesso remoto?",
  "lente": "investigar",
  "pagina_aberta": {
    "documento_id": "doc_12",
    "pagina": 4
  }
}
```

`pagina_aberta` é opcional. Sem E2B, o motor devolve excertos e miniaturas; `frase` não aparece.

**Resposta** `200` + `text/event-stream`

```json
{"tipo": "miniaturas", "itens": [{"documento_id": "doc_12", "pagina": 4, "url": "/media/thumbs/doc_12_p4.webp"}]}
```

```json
{
  "tipo": "excerto",
  "n": 1,
  "documento_id": "doc_12",
  "pagina": 4,
  "texto": "O acesso remoto exige aprovação do responsável de segurança.",
  "offsets": {"inicio": 120, "fim": 188},
  "caixas": [{"pagina": 4, "x": 0.1, "y": 0.4, "w": 0.7, "h": 0.03}],
  "score_juiz": 0.82
}
```

```json
{
  "tipo": "frase",
  "texto": "O acesso remoto exige aprovação do responsável de segurança. [1]",
  "citacoes": [1]
}
```

```json
{"tipo": "vazio", "motivo": "nenhuma_frase_acima_do_limiar"}
```

```json
{"tipo": "fim", "mensagem_id": "msg_90"}
```

### HTTP-correlate

`POST /correlate`

**Pedido**

```json
{
  "chat_id": "cht_01",
  "conceito_a": "controlo de acessos",
  "conceito_b": "registo de auditoria",
  "lente": "investigar"
}
```

**Resposta** stream como em `HTTP-search`, com excertos etiquetados:

```json
{
  "tipo": "excerto",
  "n": 2,
  "papel": "A",
  "documento_id": "doc_3",
  "pagina": 2,
  "texto": "O controlo de acessos revê-se anualmente.",
  "offsets": {"inicio": 10, "fim": 52},
  "caixas": [],
  "score_juiz": 0.77
}
```

`papel`: `A` \| `B` \| `relacao`.

### HTTP-confront

`POST /confront`

Sem E2B. Leitura determinística (juiz nas duas direcções + cosseno).

**Pedido**

```json
{
  "chat_id": "cht_01",
  "trecho_a": {
    "documento_id": "doc_12",
    "pagina": 4,
    "texto": "O acesso remoto exige aprovação prévia.",
    "offsets": {"inicio": 120, "fim": 160}
  },
  "trecho_b": {
    "documento_id": "doc_8",
    "pagina": 1,
    "texto": "Qualquer colaborador pode ligar-se à VPN sem pedido.",
    "offsets": {"inicio": 40, "fim": 95}
  }
}
```

Trechos podem ser só `texto` colado (sem `documento_id`) quando ainda não há citações.

**Resposta 200**

```json
{
  "mensagem_id": "msg_91",
  "leitura": "contradizem-se",
  "score": 0.71,
  "trecho_a": {"documento_id": "doc_12", "pagina": 4},
  "trecho_b": {"documento_id": "doc_8", "pagina": 1}
}
```

`leitura`: `concordam` \| `contradizem-se` \| `assuntos_diferentes`.

### HTTP-lacunas

`POST /lacunas`

Sem E2B. Uma mensagem com estado por linha.

**Pedido**

```json
{
  "chat_id": "cht_01",
  "linhas": [
    "Existe política de palavras-passe?",
    "Há evidência de formação anual?",
    "O plano de continuidade está assinado?"
  ],
  "lente": "acreditacao"
}
```

**Resposta 200**

```json
{
  "mensagem_id": "msg_92",
  "itens": [
    {
      "linha": "Existe política de palavras-passe?",
      "estado": "encontrado",
      "citacao": {
        "documento_id": "doc_2",
        "pagina": 3,
        "texto": "A política de palavras-passe revê-se de dois em dois anos.",
        "offsets": {"inicio": 0, "fim": 58},
        "score_juiz": 0.8
      }
    },
    {
      "linha": "Há evidência de formação anual?",
      "estado": "fraco",
      "citacao": null
    },
    {
      "linha": "O plano de continuidade está assinado?",
      "estado": "ausente",
      "citacao": null
    }
  ]
}
```

`estado`: `encontrado` \| `fraco` \| `ausente`.

---

## Chat

### HTTP-chat-list

`GET /chats`

```json
{
  "itens": [
    {"id": "cht_01", "titulo": "Quem aprova o acesso remoto?", "actualizado_em": "2026-10-25T00:10:00Z"}
  ]
}
```

### HTTP-chat-create

`POST /chats`

**Pedido** `{}` ou `{ "titulo": null }`

**Resposta 201**

```json
{"id": "cht_02", "titulo": null, "mensagens": []}
```

A primeira procura preenche o título.

### HTTP-chat-get

`GET /chats/{chat_id}`

```json
{
  "id": "cht_01",
  "titulo": "Quem aprova o acesso remoto?",
  "mensagens": [
    {"id": "msg_1", "papel": "utilizador", "texto": "Quem aprova o acesso remoto?"},
    {
      "id": "msg_90",
      "papel": "assistente",
      "frases": ["O acesso remoto exige aprovação do responsável de segurança. [1]"],
      "excertos": [{"n": 1, "documento_id": "doc_12", "pagina": 4}]
    }
  ]
}
```

### HTTP-chat-rename

`PATCH /chats/{chat_id}`

**Pedido** `{ "titulo": "Acesso remoto" }`

**Resposta 200** `{ "id": "cht_01", "titulo": "Acesso remoto" }`

### HTTP-chat-delete

`DELETE /chats/{chat_id}`

**Resposta 204** corpo vazio.

### HTTP-chat-pin-excerpt

`POST /chats/{chat_id}/fixados`

Fixa um trecho na conversa (linha no SQLite) para reabrir sem nova procura.

**Pedido**

```json
{
  "documento_id": "doc_12",
  "pagina": 4,
  "texto": "O acesso remoto exige aprovação do responsável de segurança.",
  "offsets": {"inicio": 120, "fim": 188}
}
```

**Resposta 201** `{ "id": "fix_1" }`

---

## Leitor

### HTTP-reader-document

`GET /documents/{documento_id}`

```json
{
  "id": "doc_12",
  "titulo": "Politica de acesso remoto",
  "tipo": "pdf",
  "paginas": 12,
  "hash_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "desactualizado": false,
  "sumario": [{"titulo": "1. Âmbito", "pagina": 1}],
  "etiquetas": ["acesso"]
}
```

`hash_sha256` é hex SHA-256 (64 caracteres); o valor acima é sintético.

### HTTP-reader-pages

`GET /documents/{documento_id}/pages/{pagina}`

```json
{
  "pagina": 4,
  "texto": "…texto da página…",
  "largura": 595,
  "altura": 842
}
```

Bytes da página ou imagem: `GET /documents/{documento_id}/pages/{pagina}/render` → `image/webp` (ou tipo acordado na implementação).

### HTTP-reader-highlights

`GET /documents/{documento_id}/highlights?mensagem_id=msg_90`

```json
{
  "itens": [
    {
      "n": 1,
      "pagina": 4,
      "offsets": {"inicio": 120, "fim": 188},
      "caixas": [{"pagina": 4, "x": 0.1, "y": 0.4, "w": 0.7, "h": 0.03}],
      "mensagem_id": "msg_90"
    }
  ]
}
```

---

## Dossier

### HTTP-dossier-close

`POST /chats/{chat_id}/dossier`

Fecho explícito (botão). Grava fotografia no SQLite: perguntas, frases no ecrã, trechos, ficheiro, página, offsets, caixas, score do juiz, SHA-256, data, versões dos modelos.

**Pedido** `{}`

**Resposta 201**

```json
{
  "id": "dos_1",
  "fechado_em": "2026-10-25T00:20:00Z",
  "versoes": {
    "embedding": "embeddinggemma-2",
    "juiz": "mmarco-minilm-onnx-int8",
    "juiz_lora": null,
    "escritor": "gemma-4-e2b-qat-q4"
  }
}
```

### HTTP-dossier-get

`GET /dossiers/{dossier_id}`

Reabrir lê a fotografia. Se o hash em disco divergir, `fonte_alterada: true`; a prova antiga mantém-se.

```json
{
  "id": "dos_1",
  "chat_id": "cht_01",
  "fonte_alterada": false,
  "frases": [
    {
      "texto": "O acesso remoto exige aprovação do responsável de segurança. [1]",
      "trecho": "O acesso remoto exige aprovação do responsável de segurança.",
      "documento_id": "doc_12",
      "pagina": 4,
      "hash_sha256_fecho": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "score_juiz": 0.82
    }
  ]
}
```

### HTTP-dossier-export

`GET /dossiers/{dossier_id}/export`

**Resposta 200** multipart ou JSON com dois artefactos:

```json
{
  "markdown_url": "/dossiers/dos_1/export.md",
  "json_url": "/dossiers/dos_1/export.json"
}
```

Markdown para leitura; JSON com os mesmos campos para arquivo.

---

## Feedback

### HTTP-feedback

`POST /feedback`

Não bloqueia a procura seguinte. `descartar` não treina.

**Pedido**

```json
{
  "mensagem_id": "msg_90",
  "accao": "acertou"
}
```

ou

```json
{
  "mensagem_id": "msg_90",
  "accao": "corrigir",
  "positivos": [
    {
      "documento_id": "doc_12",
      "pagina": 5,
      "texto": "A aprovação é do responsável de segurança da informação.",
      "offsets": {"inicio": 10, "fim": 70}
    }
  ]
}
```

`accao`: `acertou` \| `corrigir` \| `descartar`. Em `corrigir`, as marcas da resposta ficam negativas; `positivos` ficam positivos.

**Resposta 202**

```json
{"aceite": true, "treino_agendado": false}
```

`treino_agendado: true` quando o LoRA fica em fila (máquina livre).

---

## Alertas

Máximo dez. Documentos antigos não são revistos sozinhos; só frases do documento acabado de indexar.

### HTTP-alerts-list

`GET /alerts`

```json
{
  "itens": [
    {"id": "ale_1", "texto": "Novas menções a VPN", "activo": true, "chat_id": "cht_al_1"}
  ]
}
```

### HTTP-alerts-create

`POST /alerts`

**Pedido**

```json
{"texto": "Novas menções a VPN", "lente": "investigar"}
```

**Resposta 201** `{ "id": "ale_1", "chat_id": "cht_al_1", "activo": true }`

**Resposta 409** se já existem dez: `{ "erro": "limite_alertas", "mensagem": "Máximo de dez alertas." }`

### HTTP-alerts-toggle

`PATCH /alerts/{alerta_id}`

**Pedido** `{ "activo": false }`

**Resposta 200** `{ "id": "ale_1", "activo": false }`

---

## Biblioteca

### HTTP-library-list

`GET /library?etiqueta=acesso&cursor=&limite=50`

Lista virtualizada (cursor).

```json
{
  "itens": [
    {
      "id": "doc_12",
      "titulo": "Politica de acesso remoto",
      "etiquetas": ["acesso"],
      "desactualizado": false,
      "tipo_sugerido": "politica"
    }
  ],
  "cursor_seguinte": null
}
```

### HTTP-library-ingest

`POST /library/ingest`

Multipart: ficheiro; ou JSON `{ "url": "https://exemplo.invalid/artigo" }`.

**Resposta 202** `{ "documento_id": "doc_13", "estado": "na_fila" }`

URL privada → **400** `{ "erro": "url_privada", "mensagem": "Endereço privado recusado." }`.

### HTTP-library-tags

`PUT /documents/{documento_id}/tags`

**Pedido** `{ "etiquetas": ["acesso", "vpn"] }`

**Resposta 200** `{ "id": "doc_12", "etiquetas": ["acesso", "vpn"] }`

Etiquetas são manuais. A sugestão de tipo por embedding continua só sugestão.

---

## Correções (export / import)

Não entra no menu `+` da barra. Estado da aprendizagem na barra lateral.

### HTTP-corrections-export

`GET /corrections/export`

**Resposta 200**

```json
{
  "formato": 1,
  "modelo_base_id": "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
  "correcoes": [
    {
      "pergunta": "Quem aprova o acesso remoto?",
      "trecho": "O acesso remoto exige aprovação do responsável de segurança.",
      "etiqueta": "positivo",
      "lente": "investigar",
      "hash_par": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    }
  ]
}
```

Exporta o conjunto de correções, **não** o binário LoRA. O ecrã de exportação avisa que os trechos são texto dos documentos.

### HTTP-corrections-import-preview

`POST /corrections/import/preview`

**Pedido** corpo = mesmo formato do export.

**Resposta 200**

```json
{
  "contagem": 50,
  "lentes": ["investigar", "verificar"],
  "amostra_perguntas": ["Quem aprova o acesso remoto?"],
  "duplicados_ignorados": 2,
  "modelo_base_ok": true
}
```

Se `modelo_base_ok` for `false` → não se confirma; o motor recusa ficheiro de outro modelo base.

### HTTP-corrections-import-confirm

`POST /corrections/import/confirm`

**Pedido**

```json
{
  "formato": 1,
  "modelo_base_id": "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
  "correcoes": []
}
```

Nada se aplica antes desta confirmação. Pares repetidos entram uma vez. Treino = base + correções locais + importadas, quando a máquina está livre.

**Resposta 202** `{ "aceite": true, "treino_agendado": true }`

---

## Cópia de segurança

### HTTP-backup

`POST /backup`

**Pedido**

```json
{"destino": "/caminho/escolhido/lente-data.zip"}
```

O caminho é local à máquina do utilizador (diálogo da UI). Conteúdo: pasta `data/` em zip. Sem nuvem.

**Resposta 200**

```json
{"bytes": 1048576, "caminho": "/caminho/escolhido/lente-data.zip"}
```

Alternativa de implementação: `GET /backup.zip` devolve o zip e a UI guarda onde o utilizador escolher. O contrato exige zip de `data/`, sem upload remoto.

---

## Modelos

### HTTP-models-status

`GET /models/status`

```json
{
  "embedding": {"estado": "pronto", "caminho": "models/embeddinggemma-2"},
  "juiz": {"estado": "pronto", "caminho": "models/juiz-onnx-int8"},
  "escritor": {
    "estado": "em_falta",
    "caminho_esperado": "models/gemma-4-e2b-qat-q4",
    "tamanho_aprox_gb": 3
  }
}
```

`estado`: `pronto` \| `a_descarregar` \| `em_falta` \| `erro_licenca`.

### HTTP-models-guidance

`GET /models/guidance`

Quando a licença Hugging Face bloqueia ou falta ficheiro: a app abre e diz onde pôr o peso.

```json
{
  "itens": [
    {
      "modelo": "escritor",
      "mensagem": "Coloca os pesos Q4 em models/gemma-4-e2b-qat-q4. Sem o E2B o chat segue com excertos e miniaturas.",
      "url_documentacao": null
    }
  ]
}
```

### HTTP-models-download

`POST /models/download`

**Pedido** `{ "modelo": "escritor" }`

**Resposta 202** `{ "estado": "a_descarregar" }`

Se a licença bloquear: **409** com a mesma orientação de `HTTP-models-guidance`. O download não trava a UI; o escalonador trata da fila.

---

## Mapa rápido

| ID | Método | Caminho |
| --- | --- | --- |
| HTTP-health | GET | `/health` |
| HTTP-search | POST | `/search` |
| HTTP-correlate | POST | `/correlate` |
| HTTP-confront | POST | `/confront` |
| HTTP-lacunas | POST | `/lacunas` |
| HTTP-chat-list | GET | `/chats` |
| HTTP-chat-create | POST | `/chats` |
| HTTP-chat-get | GET | `/chats/{chat_id}` |
| HTTP-chat-rename | PATCH | `/chats/{chat_id}` |
| HTTP-chat-delete | DELETE | `/chats/{chat_id}` |
| HTTP-chat-pin-excerpt | POST | `/chats/{chat_id}/fixados` |
| HTTP-reader-document | GET | `/documents/{documento_id}` |
| HTTP-reader-pages | GET | `/documents/{documento_id}/pages/{pagina}` |
| HTTP-reader-highlights | GET | `/documents/{documento_id}/highlights` |
| HTTP-dossier-close | POST | `/chats/{chat_id}/dossier` |
| HTTP-dossier-get | GET | `/dossiers/{dossier_id}` |
| HTTP-dossier-export | GET | `/dossiers/{dossier_id}/export` |
| HTTP-feedback | POST | `/feedback` |
| HTTP-alerts-list | GET | `/alerts` |
| HTTP-alerts-create | POST | `/alerts` |
| HTTP-alerts-toggle | PATCH | `/alerts/{alerta_id}` |
| HTTP-library-list | GET | `/library` |
| HTTP-library-ingest | POST | `/library/ingest` |
| HTTP-library-tags | PUT | `/documents/{documento_id}/tags` |
| HTTP-corrections-export | GET | `/corrections/export` |
| HTTP-corrections-import-preview | POST | `/corrections/import/preview` |
| HTTP-corrections-import-confirm | POST | `/corrections/import/confirm` |
| HTTP-backup | POST | `/backup` |
| HTTP-models-status | GET | `/models/status` |
| HTTP-models-guidance | GET | `/models/guidance` |
| HTTP-models-download | POST | `/models/download` |
