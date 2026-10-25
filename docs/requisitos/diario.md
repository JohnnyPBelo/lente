# Diário local — `REQ-DIA`

## REQ-DIA-001

**Enunciado:** Existe um diário local, só de acrescentar, que regista procuras, documentos abertos, feedback e fechos de dossier.

**Origem:** docs/origem/plano.md — «Mais, ainda sem peso»

**Critérios de aceitação:**

1. **Dado** o utilizador realiza uma procura, abre um documento, dá feedback ou fecha um dossier, **quando** a acção completa, **então** uma entrada correspondente é acrescentada ao diário local (append-only).
2. **Dado** o diário com entradas, **quando** se tenta «editar» ou «apagar» uma entrada antiga pela via normal da app, **então** não há operação de reescrita/remoção selectiva que altere o histórico já escrito (só de acrescentar).

**Não pede:** UI rica de timeline obrigatória neste requisito; exportação do diário (pode existir via backup REQ-BAK).

---

## REQ-DIA-002

**Enunciado:** O diário não implica contas nem rede.

**Origem:** docs/origem/plano.md — «Mais, ainda sem peso»

**Critérios de aceitação:**

1. **Dado** o diário a ser escrito, **quando** se observa o comportamento de rede/auth, **então** não há login, conta remota, nem envio do diário para um serviço externo.

**Não pede:** encriptação at-rest além do que o SO oferece; multi-utilizador no mesmo diário.
