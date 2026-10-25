# Módulos

Contratos por módulo. IDs `MOD-…` alinhados com [docs/LEITURA.md](../LEITURA.md). Cada secção: responsabilidade, entradas, saídas, o que **não** faz.

---

## MOD-ingestao

**Responsabilidade.** Transformar bytes ou URL em unidades indexáveis: texto, frases com offsets e caixas, blocos ~500 tokens (sobreposição 50), SHA-256, metadados mínimos (título, páginas).

**Entradas.** Ficheiro local (texto, Markdown, `.txt`, `.docx`, PDF com texto, PDF/imagem via Tesseract) ou URL de artigo (recusa de endereços privados).

**Saídas.** Documento canónico para o índice: hash, blocos, frases (offsets, caixas), texto por página, títulos para sumário, dados para miniatura.

**Não faz.** Não embute vectores. Não corre o juiz nem o E2B. Não decide highlights. Não reavalia a biblioteca inteira. Não aceita hosts privados na URL.

---

## MOD-indice

**Responsabilidade.** Persistência de pesquisa: FTS5, vectores `sqlite-vec` (cosseno exacto, 256-d), miniaturas geradas uma vez, sumário de títulos, estado de actualização por hash.

**Entradas.** Saída da ingestão; pedido de reindexação quando o hash em disco diverge; fila de um documento de cada vez (via escalonador).

**Saídas.** Linhas e vectores no SQLite; miniaturas; marcação «desactualizado» se o ficheiro mudou; progresso da fila.

**Não faz.** Não faz pesquisa aproximada (ANN). Não usa Qdrant, Chroma, LanceDB ou Postgres. Não renderiza PDF ao passar o rato. Não corre modelos de prosa.

---

## MOD-pesquisa

**Responsabilidade.** Trazer candidatos: fusão por rank recíproco de FTS5 e embedding; prefixos EmbeddingGemma por lente; correlacionar (A/B); lacunas (lista encontrado/fraco/ausente). Identificador literal fura o chão de cosseno.

**Entradas.** Consulta (e Conceito A/B ou linhas de lacunas); lente activa; opcionalmente página aberta no leitor; histórico recente do chat só para reescrever seguimento.

**Saídas.** Lista ordenada de trechos/frases candidatas (ficheiro, página, offsets, scores); para correlacionar, etiquetas A/B/relação; para lacunas, estado por linha. Sem prosa.

**Não faz.** Não marca highlights finais (isso é o juiz). Não chama o E2B. Não injecta respostas antigas como conhecimento. Não revê documentos antigos em alertas (só o documento acabado de indexar).

---

## MOD-juiz

**Responsabilidade.** Decisão rápida sem prosa: highlight, segunda porta da frase citação, confronto (concordam / contradizem-se / assuntos diferentes), vigilância de alertas em frases novas. Feedback → ajuste imediato de ordenação/limiar; LoRA rank 8 quando livre.

**Entradas.** Pares pergunta–trecho ou frase–trecho; par de trechos no confronto; frases de documento novo no alerta; correções (acertou / corrigir / descartar); pacotes importados após confirmação.

**Saídas.** Scores e passagem/falha; leitura do confronto; mensagens de alerta quando passa; ONNX actualizado após treino aceite; export JSON de correções (não pesos LoRA).

**Não faz.** Não escreve a resposta. Não faz fine-tune do E2B. Não media ficheiros LoRA de sítios diferentes. Não aplica import antes da confirmação. Não é o Jev nem um clone local dele.

---

## MOD-escritor

**Responsabilidade.** Gemma 4 E2B QAT Q4: prosa presa aos trechos desta procura. Duas portas antes de a frase aparecer no fio: citação `[n]` no pacote; juiz confirma fidelidade. Miniaturas podem sair primeiro; sem prosa provisória a apagar.

**Entradas.** Trechos que o juiz deixou passar (+ texto dessas páginas); pergunta; lente (instrução de prosa); página aberta se a pergunta for sobre ela.

**Saídas.** Frases aceites com `[n]`; ou aviso de vazio / só excertos e miniaturas se nada sobreviver. Sem E2B: excertos e miniaturas.

**Não faz.** Não vê a biblioteca inteira. Não vê prosa anterior nem exemplos confirmados. Não corre em alerta nem lacunas. Não treina com feedback. Não descarrega os 11 GB de pesos de treino do E2B.

---

## MOD-escalonador

**Responsabilidade.** Orçamento da máquina: um trabalho pesado de cada vez; procura pausa indexação e treino; retoma no fim; deixa ≥2 núcleos livres; limita o E2B aos núcleos de escrita.

**Entradas.** Pedidos de procura, indexação, LoRA, download de modelo; sinais de ocupação.

**Saídas.** Filas e prioridades; pausa/retoma; afinação de threads/cores.

**Não faz.** Não interpreta consultas. Não decide conteúdo de highlights. Não sincroniza com a nuvem. Não reavalia a biblioteca em fundo sem pedido.

---

## MOD-armazenamento

**Responsabilidade.** Um SQLite em `data/` com `sqlite-vec` e FTS5: documentos, chats, feedback, dossiers (fotografia no fecho), alertas, diário append-only, etiquetas, hashes. Backup = zip de `data/`.

**Entradas.** Escritas dos outros módulos; pedido de export/import de correções; fecho/export de dossier; cópia de segurança.

**Saídas.** Leituras consistentes; Markdown+JSON no export de dossier; JSON de correções; zip de backup; diário só de acrescentar.

**Não faz.** Não é um segundo processo de base de dados. Não tem contas nem rede. Não guarda pesos de modelos (esses vão a `models/`).

---

## MOD-api

**Responsabilidade.** HTTP em `127.0.0.1:4317`: UI estática + JSON/SSE do [contrato-http.md](contrato-http.md). Ponto único entre React e o motor.

**Entradas.** Pedidos HTTP locais; artefacto de build de `apps/ui/`.

**Saídas.** Respostas JSON, streams de frases aceites, ficheiros de export, estados de modelo e saúde.

**Não faz.** Não escuta em `0.0.0.0` nem noutro porto por omissão. Não autentica utilizadores. Não expõe a app à rede.

---

## MOD-ui

**Responsabilidade.** Chat, barra (`+` / `/`: procurar, correlacionar, confrontar, alerta, lacunas), lente, leque, leitor (scroll, highlights, zoom, sumário, fixar trecho), barra lateral (conversas, alertas, estado de aprendizagem), feedback, dossiers, biblioteca virtualizada, estados vazios. Português. Vidro no chrome; serif no texto do leitor.

**Entradas.** Respostas da API; gestos do utilizador; `prefers-reduced-motion`.

**Saídas.** Pedidos HTTP; feedback; fechos de dossier; etiquetas; export/import de correções; pedido de backup.

**Não faz.** Não corre modelos. Não escreve no SQLite directamente. Não é Electron. Não tem segundo servidor Node em produção.
