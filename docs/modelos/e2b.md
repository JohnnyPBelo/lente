# MOD-e2b — Gemma 4 E2B QAT Q4 (escritor)

**Papel:** escrever a prosa citada. Congelado. **Visita** (sobe para a resposta, desce a seguir).

## Identidade

| Campo | Valor |
| --- | --- |
| Hugging Face | [`google/gemma-4-E2B-it-qat-q4_0-gguf`](https://huggingface.co/google/gemma-4-E2B-it-qat-q4_0-gguf) |
| Formato de runtime | GGUF QAT Q4_0 |
| Disco (artefacto de runtime) | cerca de **2,9 GB** |
| Residência | **Visita** — não fica residente entre respostas |
| Fine-tune / LoRA | **Proibido** |
| Congelado | Sim |

## O que se descarrega e o que não

| Artefacto | Acção |
| --- | --- |
| GGUF QAT Q4_0 deste id (~2,9 GB) | Descarregar para runtime |
| Pesos BF16 / unquantized de treino (~**11,4 GB**) | **Não descarregar** |

O plano e o orçamento de 16 GB assumem o Q4 de visita, não os ~11 GB de treino. Sem o E2B no disco, o chat segue com excertos e miniaturas.

## Congelado e visita

Em cada procura o E2B vê só:

- trechos que o juiz deixou passar **nesta** procura (ficheiro, página, texto);
- texto dessas páginas;
- a página aberta no leitor, se a pergunta for sobre ela.

Não vê: biblioteca inteira; prosa que escreveu antes; exemplos de respostas confirmadas; correcções do juiz como texto no prompt.

Perguntas anteriores no mesmo chat servem só para **reescrever** a query de seguimento. A resposta nova cita trechos **desta** volta.

Instruções de prosa por lente: [prefixos-e-lentes.md](prefixos-e-lentes.md). Filtragem: [duas-portas.md](duas-portas.md).

## Licença: pesos Gemma vs código do repo

| Âmbito | Licença |
| --- | --- |
| Texto e código do repositório Lente | **Apache-2.0** (`LICENSE` neste git) |
| Pesos do E2B | Licença publicada na **ficha Hugging Face** / [Gemma 4 license](https://ai.google.dev/gemma/docs/gemma_4_license) (ligação da ficha do modelo) |

O Apache-2.0 do repositório **não** coloca os pesos no git e **não** os redistribui. Os pesos ficam fora do controlo de versões; a app descarrega-os (ou pede o caminho se a licença HF bloquear o download). Ver [licencas.md](licencas.md).

## Fora deste contrato

- Manter o E2B residente.
- Descarregar os ~11,4 GB BF16 de treino.
- Injectar prosa anterior ou exemplos no prompt.
- Fine-tune do escritor.
- Usar o E2B em **alerta** ou **lacunas**.

## Origem

[docs/origem/plano.md](../origem/plano.md) — «Três papéis, dois residentes», «Orçamento da máquina», «A resposta, sem reaproveitar respostas velhas».
