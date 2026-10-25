# Modelo de processos

## Inventário

| Processo | Quando existe | Responsabilidade |
| --- | --- | --- |
| Motor Python | Runtime (sempre, enquanto a app corre) | HTTP em `127.0.0.1:4317`, servir UI estática, API, SQLite, modelos, fila de trabalhos pesados |
| Browser | Runtime (cliente) | UI; não corre modelos nem escreve no SQLite directamente |
| Node 22 | **Só build** | Compilar a UI; não fica a escutar nem a servir em produção |
| Electron / segundo servidor Node | Nunca | Fora de âmbito |

Piso declarado no plano: Python 3.11+, Node 22, 16 GB de RAM. GPU, se existir, acelera o mesmo caminho de código; não há segundo modo.

## Motor Python = UI + API

```text
[Browser] --HTTP--> 127.0.0.1:4317 (Python)
                         |
                         +-- estáticos da UI (build Node prévio)
                         +-- endpoints do motor
                         +-- SQLite + sqlite-vec (mesmo processo)
                         +-- EmbeddingGemma / juiz ONNX / E2B (visita)
                         +-- escalonador de trabalhos pesados
```

Verificação: com a app a correr, `ss`/`lsof` mostra **um** listener em `127.0.0.1:4317` pertencente ao processo Python. Não há porta Node de desenvolvimento em uso normal.

## Node: build-only

1. Desenvolvedor (ou pipeline) corre o build Node 22.
2. Artefactos estáticos ficam onde o motor os serve.
3. Em runtime, Node **não** participa.

Não há hot-reload Node obrigatório no caminho de utilização; a especificação de produto é o servidor único Python.

## Trabalhos dentro do motor

O motor não lança um processo filho por tipo de trabalho. Escala **dentro** do mesmo processo via escalonador (ver [escalonador.md](escalonador.md)):

| Trabalho | Tipo | Notas |
| --- | --- | --- |
| Procura (embedding + FTS + juiz ± E2B) | Pesado | Tem prioridade; pausa indexação e treino |
| Indexação / ingestão (1 documento na fila) | Pesado | Um documento de cada vez na fila de ingestão |
| Escrita E2B | Pesado (visita de modelo) | Limitado a ≤ `nproc - 2` núcleos |
| Treino LoRA do juiz | Pesado, só com máquina livre | ≤ 2 núcleos; PyTorch temporário |
| Miniaturas | Na indexação | Imagens pequenas feitas uma vez; não no hover |

## O que o browser faz e não faz

Faz: chat, barra, leque, leitor, feedback, exportações pedidas à API.

Não faz: carregar pesos, treinar LoRA, varrer vectores, decidir highlights. Todo o estado durável passa pelo motor e pelo SQLite.

## Arranque e paragem

1. Utilizador corre o comando de arranque → processo Python sobe → escuta `127.0.0.1:4317`.
2. Modelos residentes (embedding, juiz ONNX) carregam conforme política de runtime; falha de download HF não impede a abertura (ver [falhas.md](falhas.md)).
3. Paragem do processo Python fecha o listener; o SQLite fica no disco em `data/`.
