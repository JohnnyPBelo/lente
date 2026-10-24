# Falhas e estados observáveis

Cada falha abaixo tem **sintoma na UI** e **comportamento do motor** verificáveis. Critérios no estilo Dado / Quando / Então.

## Modelo em falta ou bloqueio Hugging Face

**Dado** a licença HF ou a rede impede o download de um peso  
**Quando** a app arranca ou um papel é pedido pela primeira vez  
**Então**

- A app **abre** na mesma (`127.0.0.1:4317`).
- A UI mostra o estado «modelo a descarregar» / instruções de **onde pôr o ficheiro** manualmente.
- Sem Embedding ou sem juiz: procuras que dependem deles não inventam resultados; mostram o estado vazio adequado.
- Sem E2B: o chat **segue** com excertos e miniaturas; não bloqueia a biblioteca nem o leitor.

Não há segundo modo «online API» para substituir os pesos locais.

## URL privada recusada

**Dado** o utilizador pede ingestão de um URL  
**Quando** o anfitrião resolve para endereço privado/loopback/link-local (ou equivalente na política SEG)  
**Então**

- O motor **recusa** a URL.
- A UI mostra o estado vazio «URL recusada».
- Nenhum documento parcial fica indexado como se a página tivesse sido lida.

URLs de artigo públicos continuam permitidas.

## Hash do ficheiro mudou

### Na biblioteca (antes de dossier)

**Dado** um documento indexado com SHA-256 `H1`  
**Quando** os bytes em disco passam a ter `H2 ≠ H1`  
**Então** a biblioteca marca o documento como **desactualizado**; não responde com índice velho em silêncio. Nova indexação recalcula hash, blocos e vectores.

### No dossier fechado

**Dado** um dossier com fotografia que inclui SHA-256 `H1` do ficheiro  
**Quando** o utilizador reabre o dossier e o ficheiro em disco tem `H2 ≠ H1`  
**Então**

- O dossier **mostra** que a fonte mudou depois do fecho.
- A prova antiga (trechos, offsets, scores, versões de modelo) **mantém-se**.
- Não se voltam a correr embedding/juiz/E2B para «actualizar» a fotografia.

## Prosa toda filtrada

**Dado** o E2B devolveu frases candidatas  
**Quando** nenhuma passa a porta `[n]` **e** a porta do juiz  
**Então**

- Nenhuma prosa filtrada aparece no fio (nem provisória a ser apagada).
- Ficam os **excertos** e as **miniaturas**, ou só o aviso de vazio se também não houver trechos.
- As miniaturas podem ter chegado **antes** da tentativa de prosa.

Estado vazio associado: «prosa toda filtrada».

## Troca LoRA rejeitada

**Dado** correções suficientes e o escalonador livre para treinar  
**Quando** o LoRA rank 8 termina e o conjunto deixado de lado (hold-out) **piora** face ao ONNX actual  
**Então**

- A troca é **rejeitada**.
- O juiz activo continua a ser o **ONNX anterior**.
- O PyTorch de treino **sai** da memória.
- A procura seguinte não usa o adaptador rejeitado.

Se o hold-out não piorar: export ONNX novo, activação, libertação do PyTorch.

## Fila / slot pesado ocupado

**Dado** o escalonador está em `search`, `index` ou `lora`  
**Quando** a UI pede outro trabalho pesado que não seja a procura com prioridade  

Comportamento:

| Pedido | Comportamento verificável |
| --- | --- |
| Nova procura enquanto index/LoRA | Procura **ganha**: pausa index/LoRA; corre; retoma |
| Segunda procura enquanto `search` | Não corre em paralelo; a UI indica ocupado / espera (uma procura de cada vez) |
| Indexação pedida durante procura | Fica em fila; começa só após a procura |
| LoRA durante procura | Não inicia; só com máquina livre (`idle` sem procura) |

Feedback Acertou/Corrigir/Descartar **não** é trabalho pesado: grava-se na hora e não bloqueia a procura seguinte.

## Outros estados vazios (referência)

Alinhados ao plano; detalhe de UI em requisitos/interface:

| Estado | Gatilho |
| --- | --- |
| Biblioteca sem ficheiros | `data/` sem documentos indexados |
| Página sem texto | PDF/imagem sem texto extraível / OCR falhou |
| Conversa nova | Ainda sem procura nomeada |
| Procura sem documentos | Juiz/recuperação sem trechos acima do limiar |
| Modelo a descarregar | Pesos em falta (secção HF acima) |

## O que não é falha silenciosa

- Responder com índice cujo hash já não bate com o disco.
- Mostrar prosa que falhou as duas portas.
- Aplicar LoRA importado/malicioso **antes** da confirmação do utilizador.
- Aceitar ficheiro de correções com `id` de modelo base diferente.
- Rever documentos antigos só porque existe um alerta novo.
