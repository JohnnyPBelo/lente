# Alertas — `REQ-ALE`

## REQ-ALE-001

**Enunciado:** No modo Alerta, a barra é um campo só com o placeholder «O que queres que eu vigie?». Enviar cria o alerta.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** o modo Alerta activo, **quando** a barra é mostrada, **então** há um único campo com o placeholder «O que queres que eu vigie?».
2. **Dado** texto nesse campo e menos de dez alertas, **quando** o utilizador envia, **então** o alerta é criado.

**Não pede:** linguagem natural a ser expandida pelo E2B; calendário de vigia.

---

## REQ-ALE-002

**Enunciado:** Há no máximo dez alertas no total.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** dez alertas já existentes, **quando** o utilizador tenta criar um décimo primeiro, **então** a criação falha ou é bloqueada com feedback observável.

**Não pede:** alertas ilimitados por conversa; quotas por lente.

---

## REQ-ALE-003

**Enunciado:** Na barra lateral, por baixo das conversas, existe um grupo Alertas.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** pelo menos um alerta criado, **quando** o utilizador olha para a barra lateral, **então** vê o grupo Alertas por baixo das conversas.

**Não pede:** pastas dentro de Alertas; arrastar alertas para conversas.

---

## REQ-ALE-004

**Enunciado:** Cada alerta abre um fio próprio.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** um alerta na lista, **quando** o utilizador o selecciona, **então** abre um fio dedicado a esse alerta (separado das conversas de procura normais).

**Não pede:** misturar mensagens de alerta no chat de procura activo sem abrir o fio.

---

## REQ-ALE-005

**Enunciado:** Quando um documento novo acaba de ser indexado, o juiz olha só para as frases desse documento. Se alguma passar o alerta, cai uma mensagem nesse fio, com a miniatura.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** um alerta activo e um documento novo cuja indexação acabou de terminar, **quando** o juiz avalia as frases desse documento face ao alerta, **então** só esse documento é considerado nessa passagem.
2. **Dado** pelo menos uma frase que passa, **quando** o resultado é emitido, **então** aparece uma mensagem no fio do alerta com miniatura.

**Não pede:** chamar o E2B para redigir o alerta; varrer a biblioteca inteira (REQ-ALE-006, REQ-FOR-002).

---

## REQ-ALE-006

**Enunciado:** Documentos antigos não são revistos sozinhos pelos alertas.

**Origem:** docs/origem/plano.md — «A barra de escrita»; «De fora, porque pesa ou muda o modelo»

**Critérios de aceitação:**

1. **Dado** um alerta novo criado depois de documentos já indexados, **quando** o alerta fica activo sem novo documento, **então** a app não relê sozinha a biblioteca antiga para alimentar o fio.

**Não pede:** botão opcional de «correr agora sobre tudo» neste requisito (fora de âmbito se for reavaliação completa em fundo).

---

## REQ-ALE-007

**Enunciado:** Desligar o alerta é um interruptor no topo desse fio.

**Origem:** docs/origem/plano.md — «A barra de escrita»

**Critérios de aceitação:**

1. **Dado** um fio de alerta aberto, **quando** o utilizador usa o interruptor no topo, **então** o alerta passa a desligado e deixa de emitir mensagens em novos documentos até ser ligado de novo.

**Não pede:** apagar o histórico do fio ao desligar; silenciar todos os alertas com um único gesto global neste requisito.
