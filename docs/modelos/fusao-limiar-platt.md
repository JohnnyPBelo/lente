# MOD-fusao — RRF, limiar visível e Platt

Contrato da fusão FTS5 + embedding e da escala do juiz.

## Fusão por rank recíproco (RRF)

Candidatos de duas listas:

1. **FTS5** — termo exacto (CVE, cláusula, sigla, identificador).
2. **Embedding** — cosseno exacto 256d.

Fusão no código (não no SQLite):

\[
\operatorname{RRF}(d) = \sum_{r \in R} \frac{1}{k + \operatorname{rank}_r(d)}
\]

| Parâmetro | Valor contratado |
| --- | --- |
| \(k\) | **60** |
| Listas \(R\) | FTS5 e embedding (duas) |
| Empates | Estável por id de frase/bloco |

A lista fundida alimenta o **juiz**. Highlights só depois do juiz deixar passar.

**Identificador literal:** match exacto de identificador **fura o chão de cosseno** (não é eliminado só por semelhança média); continua sujeito ao juiz.

## Limiar visível

| Campo | Contrato |
| --- | --- |
| O quê | Limiar \(\tau\) do juiz para highlight e para a porta 2 de fidelidade |
| Onde | Visível no estado da aprendizagem / UI (valor numérico legível) |
| Valor inicial (score bruto ONNX) | \(\tau_0 = 0{,}0\) — passa se \(s \ge \tau\) |
| Após Platt | O limiar passa a aplicar-se à **probabilidade calibrada** \(p\); valor inicial de corte \(p \ge 0{,}50\), ainda **visível** e ajustável pelo mesmo sítio de UI |

O utilizador vê o número em vigor. Feedback (Acertou / Corrigir) muda ordenação imediata e, com LoRA, a pontuação; o limiar continua explícito.

## Platt após correcções suficientes

Calibração logística de Platt sobre o score bruto \(s\):

\[
p = \sigma(a \cdot s + b)
\]

| Condição | Valor |
| --- | --- |
| Correcções suficientes | **≥ 50** pares etiquetados únicos (pergunta, trecho, etiqueta) no conjunto local + importado confirmado |
| Antes disso | Sem Platt; usa-se \(s\) bruto e \(\tau_0\) |
| Dados | Só correcções do juiz (positivas e negativas); não prosa do E2B |
| Recálculo | Após LoRA aceite ou quando o conjunto de correcções cruza o limiar das 50 |

Se as correcções deixadas de fora no holdout piorarem, a troca de LoRA/ONNX é rejeitada (requisitos de feedback); Platt só se aplica sobre o juiz em vigor.

## Aceitação (observável)

1. **Dado** hits FTS5 e embedding, **quando** a fusão corre, **então** a ordenação pré-juiz é RRF com \(k=60\).
2. **Dado** a UI aberta, **quando** se consulta o limiar, **então** o valor numérico actual está visível.
3. **Dado** ≥ 50 correcções únicas, **quando** a calibração corre, **então** o juiz passa a expor \(p\) calibrada e o limiar visível aplica-se a \(p\).
4. **Dado** < 50 correcções, **quando** se procura, **então** não há ficheiro Platt activo a alterar a escala.

## Fora deste contrato

- Índice aproximado em vez de cosseno exacto.
- Pesos RRF editáveis pelo utilizador neste marco.
- Platt no EmbeddingGemma ou no E2B.

## Origem

[docs/origem/plano.md](../origem/plano.md) — «Base vectorial», «Pesquisa, sem modelo a mais»; fechos de identificador literal e escala em [docs/LEITURA.md](../LEITURA.md).
