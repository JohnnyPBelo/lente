# MOD-confronto — Leitura determinística de dois trechos

Sem modelo novo. A lente de trabalho **não** altera estas três leituras.

## Entradas

| Símbolo | Definição |
| --- | --- |
| \(A\), \(B\) | Trechos (texto literal) |
| \(\cos\) | Cosseno entre embeddings 256d L2-normalizados de \(A\) e \(B\) (mesmo EmbeddingGemma residente) |
| \(j_{AB}\) | \(\sigma(s_{AB})\), com \(s_{AB}\) = score ONNX do juiz no par \((A, B)\) (A como primeiro membro, B como segundo) |
| \(j_{BA}\) | \(\sigma(s_{BA})\) no par \((B, A)\) |
| \(\sigma\) | Sigmoid logística; \(j \in (0,1)\) |

## Limiares

| Nome | Símbolo | Valor |
| --- | --- | --- |
| Chão de assunto | \(\tau_{\mathrm{top}}\) | **0,35** |
| Acordo mútuo | \(\tau_{\mathrm{agr}}\) | **0,55** |
| Sobreposição tópica forte | \(\tau_{\mathrm{mes}}\) | **0,50** |
| Suporte fraco | \(\tau_{\mathrm{fraco}}\) | **0,40** |
| Assimetria | \(\delta\) | **0,30** |

## Regra (ordem fixa)

1. Se \(\cos < \tau_{\mathrm{top}}\) → **assuntos diferentes**.
2. Senão, se \(\min(j_{AB}, j_{BA}) \ge \tau_{\mathrm{agr}}\) → **concordam**.
3. Senão, se \(\cos \ge \tau_{\mathrm{mes}}\) e \(\max(j_{AB}, j_{BA}) \ge \tau_{\mathrm{agr}}\) e \(\lvert j_{AB} - j_{BA}\rvert \ge \delta\) → **contradizem**.
4. Senão, se \(\cos \ge \tau_{\mathrm{mes}}\) e \(\min(j_{AB}, j_{BA}) < \tau_{\mathrm{fraco}}\) → **contradizem**.
5. Senão → **assuntos diferentes**.

Rótulos na UI (PT): **concordam** / **contradizem** / **assuntos diferentes** (o plano também usa «contradizem-se»; o contrato de teste aceita ambos como o mesmo rótulo `contradizem`).

A resposta no fio mostra as duas citações, a leitura e as pontuações (\(\cos\), \(j_{AB}\), \(j_{BA}\)). Não chama o E2B.

## Exemplos sintéticos de aceitação

Frases inventadas; números fixos para testes.

### Exemplo C1 — concordam

| Campo | Valor |
| --- | --- |
| A | «O prazo de retenção dos logs é de 90 dias.» |
| B | «Os registos de auditoria conservam-se durante noventa dias.» |
| \(\cos\) | 0,82 |
| \(j_{AB}\), \(j_{BA}\) | 0,71 / 0,68 |
| Leitura esperada | **concordam** (passo 2) |

### Exemplo C2 — contradizem (assimetria)

| Campo | Valor |
| --- | --- |
| A | «A autenticação multifactor é obrigatória para todos os acessos remotos.» |
| B | «O acesso remoto por VPN dispensa o segundo factor.» |
| \(\cos\) | 0,61 |
| \(j_{AB}\), \(j_{BA}\) | 0,72 / 0,28 |
| Leitura esperada | **contradizem** (passo 3: \(\cos\ge0{,}50\), max≥0,55, Δ=0,44≥0,30) |

### Exemplo C3 — contradizem (mesmo tema, suporte mútuo fraco)

| Campo | Valor |
| --- | --- |
| A | «O inventário de activos é actualizado mensalmente.» |
| B | «Não existe inventário formal de activos na organização.» |
| \(\cos\) | 0,58 |
| \(j_{AB}\), \(j_{BA}\) | 0,22 / 0,19 |
| Leitura esperada | **contradizem** (passo 4) |

### Exemplo C4 — assuntos diferentes

| Campo | Valor |
| --- | --- |
| A | «A cifra em repouso usa AES-256.» |
| B | «O refeitório fecha às 15:00.» |
| \(\cos\) | 0,12 |
| \(j_{AB}\), \(j_{BA}\) | 0,08 / 0,07 |
| Leitura esperada | **assuntos diferentes** (passo 1) |

### Exemplo C5 — assuntos diferentes (cos médio, sem acordo)

| Campo | Valor |
| --- | --- |
| A | «O responsável pelo tratamento é a Direcção de Compliance.» |
| B | «A política de férias marca 22 dias úteis.» |
| \(\cos\) | 0,42 |
| \(j_{AB}\), \(j_{BA}\) | 0,33 / 0,31 |
| Leitura esperada | **assuntos diferentes** (passo 5) |

## Aceitação

Para cada exemplo C1–C5, **dado** os valores de \(\cos\), \(j_{AB}\) e \(j_{BA}\) da tabela, **quando** se aplica a regra, **então** a leitura é a indicada. A implementação real obtém \(\cos\) e scores do runtime; os testes de unidade da regra podem injectar os números.

## Fora deste contrato

- Modelo NLI ou LLM só para confronto.
- A lente a mudar as três leituras.
- Prosa livre do E2B no modo Confrontar.

## Origem

[docs/origem/plano.md](../origem/plano.md) — modo Confrontar em «A barra de escrita»; fecho «Confronto determinístico» em [docs/LEITURA.md](../LEITURA.md).
