# Fluxos

Diagramas de sequência dos gestos principais. Actores comuns: **UI** (browser), **Motor** (Python em `127.0.0.1:4317`), **SQLite**, **Embedding**, **Juiz** (ONNX), **E2B**, **Escalonador**.

## Procurar

Modo de repouso da barra. Uma linha; Enter envia. Lente activa muda o prefixo EmbeddingGemma e a instrução de prosa do E2B.

```mermaid
sequenceDiagram
  participant UI
  participant Motor
  participant Esc as Escalonador
  participant Emb as Embedding
  participant DB as SQLite
  participant Juiz
  participant E2B

  UI->>Motor: pergunta (+ lente)
  Motor->>Esc: pedir slot pesado (procura)
  Esc->>Esc: pausar indexação e treino
  Motor->>Emb: embed consulta (prefixo da lente)
  Motor->>DB: FTS5 + cosseno exacto (sqlite-vec)
  Motor->>Motor: fusão RRF
  Motor->>Juiz: pontuar candidatos
  Juiz-->>Motor: trechos acima do limiar
  alt há trechos
    Motor-->>UI: miniaturas / excertos (podem chegar primeiro)
    Motor->>E2B: carregar visita + trechos + texto das páginas
    E2B-->>Motor: prosa candidata
    Motor->>Juiz: porta 1 [n] + porta 2 fidelidade
    alt alguma frase sobrevive
      Motor-->>UI: prosa filtrada + links de citação
    else nenhuma frase
      Motor-->>UI: só excertos/miniaturas ou aviso vazio
    end
    Motor->>E2B: descarregar da memória
  else sem trechos
    Motor-->>UI: aviso vazio (sem documentos)
  end
  Esc->>Esc: retomar indexação/treino se houver fila
```

## Correlacionar

Dois campos: Conceito A e Conceito B. Resultado: mensagem com três cores (A, B, relação) e o mesmo leque.

```mermaid
sequenceDiagram
  participant UI
  participant Motor
  participant Esc as Escalonador
  participant Emb as Embedding
  participant DB as SQLite
  participant Juiz
  participant E2B

  UI->>Motor: conceito A + conceito B (+ lente)
  Motor->>Esc: slot pesado (procura)
  Esc->>Esc: pausar indexação e treino
  Motor->>Emb: embed A e embed B (prefixos)
  Motor->>DB: candidatos FTS/semântica para A e para B
  Motor->>Juiz: filtrar trechos A, B e de relação
  Motor-->>UI: mensagem com três cores + leque
  opt prosa
    Motor->>E2B: visita com pacote filtrado
    Motor->>Juiz: duas portas
    Motor-->>UI: prosa filtrada
    Motor->>E2B: descarregar
  end
  Esc->>Esc: retomar fila
```

## Confrontar

Sem E2B. Sem modelo novo. Leitura = função das duas direcções do juiz e do cosseno entre trechos (concordam / contradizem-se / assuntos diferentes).

```mermaid
sequenceDiagram
  participant UI
  participant Motor
  participant Juiz
  participant Emb as Embedding

  UI->>UI: escolher Trecho A e Trecho B<br/>(citações da conversa, seleção no leitor, ou texto colado)
  UI->>Motor: par (A, B)
  Motor->>Emb: vectores dos dois trechos (se preciso)
  Motor->>Juiz: A→B e B→A
  Motor->>Motor: cosseno A↔B + limiares do contrato
  Motor-->>UI: duas citações + leitura + pontuação
  Note over UI: clique numa citação abre o leitor nesse highlight
```

## Lacunas

Caixa multi-linha; uma linha por controlo/hipótese/pergunta. **Sem E2B.** Uma mensagem: encontrado / fraco / ausente. Não se repete sozinha.

```mermaid
sequenceDiagram
  participant UI
  participant Motor
  participant Esc as Escalonador
  participant Emb as Embedding
  participant DB as SQLite
  participant Juiz

  UI->>Motor: lista de linhas (+ lente)
  Motor->>Esc: slot pesado (procura em lote)
  Esc->>Esc: pausar indexação e treino
  loop cada linha (até ~20–30)
    Motor->>Emb: embed da linha
    Motor->>DB: FTS + cosseno
    Motor->>Juiz: classificar encontrado / fraco / ausente
  end
  Motor-->>UI: uma mensagem com a lista + citações
  Note over Motor: E2B não é chamado
  Esc->>Esc: retomar fila
```

## Alerta ao indexar documento novo

Criação do alerta: campo «O que queres que eu vigie?»; máximo dez. Documentos **antigos** não são revistos sozinhos. Só o documento que acaba de ser indexado.

```mermaid
sequenceDiagram
  participant Ing as Ingestão
  participant Esc as Escalonador
  participant DB as SQLite
  participant Juiz
  participant UI

  Ing->>Esc: documento novo na fila (1 de cada vez)
  Esc->>Ing: processar (hash, blocos, frases, embed, FTS, miniatura)
  Ing->>DB: gravar documento indexado
  Ing->>DB: listar alertas activos (≤10)
  loop cada alerta activo
    Juiz->>Juiz: só frases deste documento vs texto do alerta
    alt alguma frase passa
      Ing->>DB: mensagem no fio do alerta + miniatura
      Ing-->>UI: actualizar fio Alertas (se aberto)
    end
  end
```

## Fechar dossier

Botão explícito — não automático por mensagem. Fotografia no SQLite; **não** volta a correr modelos.

```mermaid
sequenceDiagram
  participant UI
  participant Motor
  participant DB as SQLite

  UI->>Motor: fechar dossier (chat actual)
  Motor->>DB: ler mensagens, frases que passaram as duas portas,<br/>trechos, offsets, caixas, scores
  Motor->>DB: SHA-256 actual de cada ficheiro citado
  Motor->>DB: versões EmbeddingGemma, juiz (± LoRA), E2B + data
  Motor->>DB: gravar fotografia imutável do dossier
  Motor-->>UI: dossier fechado
  Note over UI,DB: Reabrir lê a fotografia.<br/>Se hash em disco ≠ hash gravado → aviso «fonte mudou»; prova antiga mantém-se.
```

## Feedback imediato

Linha Acertou / Corrigir / Descartar. Não bloqueia a procura seguinte. Não altera o E2B.

```mermaid
sequenceDiagram
  participant UI
  participant Motor
  participant DB as SQLite

  UI->>Motor: Acertou | Corrigir | Descartar
  alt Descartar
    Motor-->>UI: sem treino; link discreto para corrigir mais tarde
  else Acertou
    Motor->>DB: marcar trechos mostrados como positivos do juiz
    Motor-->>UI: na hora: próximas procuras parecidas privilegiam confirmados
  else Corrigir
    UI->>UI: abrir leitor, seleccionar trecho correcto
    Motor->>DB: marcas desta resposta → negativas; selecção → positiva
    Motor-->>UI: reordenação imediata entre candidatos já recuperados
  end
  Note over Motor: Não se injecta texto no escritor.<br/>LoRA só quando a máquina está livre (fluxo seguinte).
```

## LoRA quando a máquina está livre

Rank 8, LR baixo, puxão para o base. ≤ 2 núcleos. Se o hold-out piorar, a troca é rejeitada. Até exportar ONNX novo, a procura usa o ONNX anterior.

```mermaid
sequenceDiagram
  participant Esc as Escalonador
  participant Train as Treino LoRA
  participant DB as SQLite
  participant ONNX as Juiz ONNX activo

  Esc->>Esc: sem procura activa; fila pesada livre
  Esc->>Train: iniciar LoRA (≤2 núcleos)
  Train->>DB: carregar correções (locais + importadas confirmadas)
  Train->>Train: PyTorch temporário; treinar a partir do base
  alt hold-out não piora
    Train->>ONNX: exportar ONNX novo; activar
    Train->>Train: libertar PyTorch da memória
  else hold-out piora
    Train->>ONNX: rejeitar troca; manter ONNX anterior
    Train->>Train: libertar PyTorch
  end
  Note over Esc: Se chegar uma procura, o escalonador pausa/cancela<br/>o treino conforme a política de «procura tem prioridade».
```
