# Orçamento de máquina

Alvo: portátil com **16 GB de RAM**, com ou sem GPU. A GPU acelera o mesmo código; não há segundo modo. A máquina não deve ficar presa (reserva de núcleos em [escalonador.md](escalonador.md)).

## Memória residente durante uma procura

Componentes que **permanecem** carregados enquanto o utilizador pesquisa:

| Componente | Notas |
| --- | --- |
| Sistema operativo | Fora do controlo da app; razão dos ≥2 núcleos livres |
| Browser | Cliente da UI |
| EmbeddingGemma 2 (270M, texto) | Float32 em CPU (float16 → NaN); vector de trabalho 256-d |
| Juiz ONNX int8 (~120 MB em disco) | Residente; sem PyTorch no caminho quente |
| SQLite + `sqlite-vec` + FTS5 | Mesmo processo Python |

**Não** residentes na procura:

| Componente | Política |
| --- | --- |
| Gemma 4 E2B QAT Q4 | Visita: sobe para escrever, desce a seguir |
| Pesos de treino E2B (~11 GB) | **Não** se descarregam |
| PyTorch do juiz | Só durante LoRA; sai da memória no fim do treino |
| Visão / áudio EmbeddingGemma | Nunca carregados |

## Escritor = visita

Ciclo verificável por procura com prosa:

1. Trechos passam o juiz.
2. E2B carrega (ou reutiliza se ainda em memória **só** durante essa resposta — política preferida: descer a seguir).
3. Gera candidatos.
4. Duas portas filtram.
5. E2B liberta-se da RAM residente.

Respostas anteriores **não** entram no prompt. Sem E2B em disco/RAM: chat segue com excertos e miniaturas.

## Tetos de disco (pesos)

Ordens de grandeza do plano; verificáveis por tamanho dos artefactos em cache local:

| Artefacto | Teto aproximado |
| --- | --- |
| EmbeddingGemma (texto) | ~**2 GB** |
| Juiz ONNX int8 (+ eventual export LoRA) | ~**0,5 GB** |
| E2B QAT Q4 (inferência) | ~**3 GB** |
| Pesos de treino E2B | Fora de âmbito — não descarregar |

Soma típica dos três úteis ≪ 16 GB de RAM se o E2B for visita e o sistema+browser tiverem a sua fatia.

## Disco de dados (não pesos)

| Conteúdo | Onde |
| --- | --- |
| SQLite (docs, vectores, FTS, chats, feedback, dossiers, alertas, diário) | `data/` |
| Miniaturas | Geradas na indexação; guardadas com a biblioteca |
| Cópia de segurança | Zip da pasta `data/` no sítio escolhido pelo utilizador |

Uma cópia do ficheiro SQLite leva vectores e FTS consigo.

## Orçamento de CPU (resumo)

Repete [escalonador.md](escalonador.md) para fecho de verificação:

- Sempre ≥ 2 núcleos livres para sistema + UI.
- E2B ≤ `nproc - 2`.
- LoRA ≤ 2 núcleos.
- Um trabalho pesado de cada vez; procura pausa indexação e treino.

## O que o orçamento proíbe

- Base vectorial noutro processo (dobra RAM e complexidade).
- Índice aproximado que poupa CPU omitindo vizinhos.
- Manter E2B residente «por comodidade» entre conversas.
- Carregar clone local tipo Qwen ~4B (~9 GB) ou DeBERTa grande (~1 GB) **por cima** dos três papéis — fora de âmbito como System One.
- Reavaliar a biblioteca inteira em fundo (alerta só olha o documento acabado de indexar).
