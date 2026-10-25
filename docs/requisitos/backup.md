# Cópia de segurança — `REQ-BAK`

## REQ-BAK-001

**Enunciado:** Existe uma acção de cópia de segurança que coloca a pasta `data/` num zip, no sítio que o utilizador escolher.

**Origem:** docs/origem/plano.md — «Mais, ainda sem peso»

**Critérios de aceitação:**

1. **Dado** a app com dados em `data/`, **quando** o utilizador corre a acção de cópia de segurança e escolhe um destino, **então** é criado um ficheiro zip contendo o conteúdo de `data/` nesse destino.

**Não pede:** backup incremental; agendamento automático; incluir pesos de modelos fora de `data/` salvo se estiverem dentro de `data/`.

---

## REQ-BAK-002

**Enunciado:** A cópia de segurança é local — sem nuvem.

**Origem:** docs/origem/plano.md — «Mais, ainda sem peso»

**Critérios de aceitação:**

1. **Dado** a acção de cópia de segurança, **quando** o utilizador a executa, **então** o destino é um caminho local escolhido por si e não há upload automático para um serviço de nuvem da app.

**Não pede:** restauro guiado completo neste requisito (pode ser manual via descompactar); sync contínuo.
