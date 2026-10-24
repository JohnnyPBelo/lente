# Segurança e superfície local — `REQ-SEG`

## REQ-SEG-001

**Enunciado:** A ingestão por URL recusa endereços privados (SSRF local).

**Origem:** docs/origem/plano.md — «Entradas»; alinhado a REQ-ING-007

**Critérios de aceitação:**

1. **Dado** uma URL que resolve para endereço privado ou de loopback, **quando** o utilizador a submete, **então** a pedido é recusado e não há fetch interno a esse alvo.

**Não pede:** firewall de sistema; lista branca de domínio corporativo.

---

## REQ-SEG-002

**Enunciado:** O serviço escuta em `127.0.0.1:4317`, não exposto na rede local por omissão.

**Origem:** docs/origem/plano.md — «Como corre»; fecho de lacuna (LEITURA — «Um só servidor»)

**Critérios de aceitação:**

1. **Dado** o arranque por omissão, **quando** se inspecciona o bind do servidor, **então** está em `127.0.0.1:4317` (não `0.0.0.0` por defeito).

**Não pede:** autenticação mutual TLS; reverse proxy.

---

## REQ-SEG-003

**Enunciado:** Não há contas, permissões multi-utilizador nem sincronização em rede.

**Origem:** docs/origem/plano.md — «Mais, ainda sem peso»; «De fora, porque pesa ou muda o modelo»

**Critérios de aceitação:**

1. **Dado** a app em uso, **quando** o utilizador procura login, permissões partilhadas ou sync, **então** essas funções não existem no produto.

**Não pede:** ACL em ficheiros do SO; multi-seat.

---

## REQ-SEG-004

**Enunciado:** Importar correções não aplica nada antes da confirmação explícita do utilizador.

**Origem:** docs/origem/plano.md — «Juntar afinações»; alinhado a REQ-FBK-014 e REQ-FBK-016

**Critérios de aceitação:**

1. **Dado** um ficheiro de correções seleccionado, **quando** ainda não houve confirmação, **então** o juiz em produção não incorpora esses exemplos.

**Não pede:** assinatura digital dos JSON de correções; scanning de malware.

---

## REQ-SEG-005

**Enunciado:** O diário e os dados de prova ficam locais; a cópia de segurança não envia para a nuvem.

**Origem:** docs/origem/plano.md — «Mais, ainda sem peso»; REQ-DIA-002; REQ-BAK-002

**Critérios de aceitação:**

1. **Dado** diário, SQLite e backup, **quando** o utilizador usa a app sem configurar serviços externos, **então** não há upload automático desses dados.

**Não pede:** encriptação E2E; wipe remoto.

---

## REQ-SEG-006

**Enunciado:** A geração de procedimentos de ataque está fora de âmbito e não é um modo da app (ver REQ-FOR-010). A app não oferece fluxo dedicado a produzir playbooks ofensivos.

**Origem:** docs/origem/plano.md — «De fora, porque pesa ou muda o modelo»

**Critérios de aceitação:**

1. **Dado** a UI e os modos da barra, **quando** se inventariam funcionalidades, **então** não existe modo ou lente cujo propósito declarado seja gerar procedimentos de ataque.

**Não pede:** filtro de conteúdo genérico em todas as perguntas do utilizador sobre segurança defensiva; censura de documentos do utilizador já na biblioteca.
