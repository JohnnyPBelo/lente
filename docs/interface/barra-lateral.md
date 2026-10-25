# Barra lateral

Origem: `docs/origem/plano.md` — «O chat e o leitor»; «A barra de escrita» (Alertas; Exportar/Importar). Requisitos: `REQ-CHT-001`, `REQ-ALE-*`, `REQ-FBK-*` (exportação).

Chrome em **vidro líquido** ([principios.md](principios.md)).

## Estrutura de cima para baixo

1. **Estado da aprendizagem** (topo)
2. **Conversas** (lista + nova)
3. **Alertas** (grupo por baixo das conversas)

## Estado da aprendizagem (topo)

Sem campo de texto. Duas acções:

| Acção | Papel |
| --- | --- |
| **Exportar correções** | Exporta o JSON de correções do juiz (não o binário LoRA) |
| **Importar correções** | Mostra contagem, lentes e amostra de perguntas; só treina após confirmação |

O ecrã de exportação **avisa** que os trechos são texto dos documentos e **saem da máquina**. Copy: [copy.md](copy.md).

Importar: pares repetidos uma vez; ficheiro de outro modelo base **recusado**; nada se aplica antes da confirmação.

Estas acções **não** estão no menu `+` / `/` da barra de escrita.

## Conversas — CRUD

| Acção | Comportamento |
| --- | --- |
| Nova | Cria conversa vazia (estado de conversa nova) |
| Abrir | Mostra o fio |
| Renomear | Edita o nome |
| Apagar | Remove a conversa |
| Nome automático | A **primeira procura** dá o nome se ainda não houver |

Lista em vidro; item activo distinguível sem cartão pesado.

## Grupo Alertas

- Aparece **por baixo** das conversas.
- Cada alerta abre um **fio próprio**.
- No topo do fio: **interruptor** para ligar/desligar o alerta (desligado → deixa de emitir em documentos novos).
- Mensagens do alerta: quando um documento **novo** acaba de indexar e o juiz encontra frases que passam; com **miniatura**. Documentos antigos **não** são revistos sozinhos.
- Máximo **dez** alertas no total (criação bloqueada além disso — copy em [copy.md](copy.md)).

## O que a barra lateral não faz

- Pastas aninhadas de conversas (além do agrupamento Conversas / Alertas).
- Exportar/Importar no menu da barra de escrita.
- Contas, sync ou avatares de utilizador.
