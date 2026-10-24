# Desempenho e orçamento — `REQ-DES`

## REQ-DES-001

**Enunciado:** Com milhares de documentos e vectores de 256 dimensões, o varrimento de cosseno exacto cabe em milissegundos no alvo de escala. Se deixar de caber, a correcção mantém-se exacta — não se troca por índice aproximado.

**Origem:** docs/origem/plano.md — «Base vectorial»; fecho de lacuna (LEITURA — «Escala»)

**Critérios de aceitação:**

1. **Dado** um corpus na ordem de milhares de documentos com vectores 256-d, **quando** se corre uma procura semântica no hardware alvo (16 GB), **então** a fase de varrimento de cosseno completa-se em milissegundos (ordem de grandeza compatível com UI interactiva).
2. **Dado** um corpus em que o varrimento já não cabe confortavelmente em milissegundos, **quando** se escolhe a estratégia de escala, **então** continua-se com cosseno exacto (optimizações sem ANN) e não se adopta índice aproximado.

**Não pede:** SLA formal em percentis P99 publicados; sharding multi-máquina.

---

## REQ-DES-002

**Enunciado:** A lista da biblioteca virtualizada mantém a UI utilizável com milhares de ficheiros.

**Origem:** docs/origem/plano.md — «Pesquisa, sem modelo a mais»; alinhado a REQ-BIB-003

**Critérios de aceitação:**

1. **Dado** milhares de entradas na biblioteca, **quando** o utilizador faz scroll contínuo na lista, **então** a interface permanece utilizável (sem congelar o processo de UI por montar todas as linhas).

**Não pede:** virtualização do fio de chat neste requisito; infinite scroll remoto.

---

## REQ-DES-003

**Enunciado:** Orçamento de máquina: um trabalho pesado de cada vez; pelo menos dois núcleos livres; miniaturas feitas uma vez na indexação (sem re-render de PDF no hover).

**Origem:** docs/origem/plano.md — «Orçamento da máquina»

**Critérios de aceitação:**

1. **Dado** procura vs. indexação/treino, **quando** ambos seriam pesados, **então** não correm em pleno a simultâneo — a procura tem prioridade com pausa/retoma (REQ-BUS-012 / REQ-MOD-004).
2. **Dado** o leque com miniaturas, **quando** o utilizador passa o rato / abre o leque, **então** as imagens usadas são as geradas na indexação, não um render completo do PDF por hover.

**Não pede:** profiler integrado; métricas Prometheus.
