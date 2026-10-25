# MOD-portas — Duas portas da prosa

Nenhuma frase do E2B aparece no fio sem passar as duas portas. Miniaturas e excertos podem aparecer **antes**. **Não há prosa provisória** a ser apagada depois.

## Porta 1 — citação `[n]`

| Regra | Detalhe |
| --- | --- |
| Forma | A frase termina com `[n]`, `n` inteiro ≥ 1 |
| Pacote | `n` indexa um trecho que estava no **pacote desta procura** (aprovado pelo juiz para esta volta) |
| Falha | Sem `[n]`, ou `n` fora do pacote → a frase **sai** |

Não se reescreve a frase automaticamente para acrescentar a citação. Não se citam documentos fora do pacote.

## Porta 2 — fidelidade do juiz

| Regra | Detalhe |
| --- | --- |
| Entrada | Frase que já passou a porta 1 + trecho citado `[n]` |
| Modelo | O mesmo juiz ONNX ([juiz.md](juiz.md)) |
| Critério | Pontuação frase↔trecho ≥ limiar de fidelidade (ver [fusao-limiar-platt.md](fusao-limiar-platt.md); limiar visível) |
| Falha | Abaixo do limiar → a frase **sai** |

## Ordem e UX

```text
E2B gera candidatos de prosa
        │
        ▼
  Porta 1: [n] no pacote?  ──não──► descarta frase
        │sim
        ▼
  Porta 2: juiz fiel?      ──não──► descarta frase
        │sim
        ▼
  Frase entra no fio (só agora)
```

- Miniaturas dos documentos podem mostrar-se primeiro.
- Streaming: bufferiza prosa até às portas; **não** emite tokens crus no chat para depois os remover.
- Se nenhuma frase sobreviver: ficam excertos e miniaturas, ou só o aviso de vazio.

## Aceitação (observável)

1. **Dado** frases do E2B sem `[n]` válido, **quando** as portas correm, **então** essas frases não aparecem no fio.
2. **Dado** frase com `[n]` válido mas juiz abaixo do limiar de fidelidade, **quando** passa a porta 2, **então** a frase não aparece.
3. **Dado** procura em curso, **quando** as miniaturas já estão visíveis e as portas ainda não terminaram, **então** não há prosa no fio que depois desapareça.

## Fora deste contrato

- Mostrar prosa só com a porta 1.
- Regenerar automaticamente até haver prosa.
- Usar um segundo modelo só para a porta 2.

## Origem

[docs/origem/plano.md](../origem/plano.md) — «A resposta, sem reaproveitar respostas velhas»; fecho «Frase só depois das duas portas» em [docs/LEITURA.md](../LEITURA.md).
