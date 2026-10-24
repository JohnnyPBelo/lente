# Como ler esta especificação

## Fonte de verdade

[docs/origem/plano.md](origem/plano.md) é o plano aceite em 24–25 de outubro de 2026 (Lisboa). Não o reescrever. Tudo o resto deriva dele ou fecha lacunas que ele deixa explícitas.

[docs/origem/LEIA-ME.md](origem/LEIA-ME.md) descreve o pacote do plano.

## Esquema de IDs

| Prefixo | Significado | Exemplo |
| --- | --- | --- |
| `ADR-NNN` | Decisão de arquitectura | `ADR-001` |
| `REQ-AAA-NNN` | Requisito (área + número) | `REQ-ING-001` |
| `PLN-NN` | Plano de implementação | `PLN-01` |
| `MOD-…` | Contrato de módulo | `MOD-juiz` |
| `HTTP-…` | Endpoint do contrato HTTP | `HTTP-search` |

Áreas de requisito: `ING` ingestão, `BUS` pesquisa, `JUI` juiz, `RES` resposta, `CHT` chat/runtime de UI, `BAR` barra, `LEI` leitor, `DOS` dossier, `FBK` feedback, `BIB` biblioteca, `ALE` alertas, `DIA` diário, `BAK` cópia de segurança, `MOD` runtime de modelos, `VAZ` estados vazios, `A11` acessibilidade, `SEG` segurança, `DES` desempenho, `FOR` fora de âmbito.

## Regra de aceitação

Um requisito está cumprido quando os critérios **Dado / Quando / Então** desse requisito passam. Um plano de implementação está feito quando todas as caixas do plano estão marcadas e os testes nomeados passam. Uma secção de `docs/origem/plano.md` sem destino na matriz de rastreio é um buraco: fecha-se antes de o PR de rastreio ficar pronto.

Critérios usam frases observáveis. Sem «robusto», «rápido» ou «intuitivo» sem número ou gesto verificável.

## Decisões de fecho (lacunas do plano de origem)

O plano de origem não chega a estas regras. Ficam escritas como ADRs, para o revisor as poder recusar.

1. **Um só servidor.** O motor Python escuta em `127.0.0.1:4317` e serve a UI já construída. Node 22 constrói a UI. Não há Electron.
2. **Frase só depois das duas portas.** A prosa só aparece no fio depois de passar a citação `[n]` e o juiz. As miniaturas podem aparecer primeiro. Não há prosa provisória a ser apagada.
3. **Blocos e frases.** Unidade de embedding: bloco de cerca de 500 tokens do tokenizador do EmbeddingGemma, sobreposição de 50. Unidade de highlight e de julgamento: a frase, com offsets e caixas gravados na ingestão.
4. **Lentes → prefixos EmbeddingGemma 2.** Procurar curto: `task: search result`. Investigar e acreditação: `task: question answering`. Verificar e assessment: `task: fact checking`. Documentos: `title: {título} | text: {conteúdo}`. A instrução de prosa de cada lente só entra no E2B. Alerta e lacunas não chamam o E2B.
5. **Confronto determinístico.** Sem modelo novo. A leitura (concordam / contradizem-se / assuntos diferentes) é função das duas direcções do juiz e do cosseno entre os dois trechos. Limiares e exemplos sintéticos ficam no contrato do confronto.
6. **Identificador literal.** Fura o chão de cosseno; continua sujeito ao juiz.
7. **Escala.** Milhares de documentos, cosseno exacto. Se o varrimento deixar de caber em milissegundos, a correcção mantém-se; não se troca por índice aproximado.

## Ordem de leitura sugerida

1. `docs/origem/plano.md`
2. Este ficheiro
3. `docs/decisoes/`
4. `docs/requisitos/`
5. `docs/arquitetura/`, `docs/dados/`, `docs/modelos/`, `docs/interface/`, `docs/estrutura/`
6. `docs/planos/` na ordem `PLN-01` … `PLN-21`
7. `docs/rastreio/matriz.md`

## Exemplos sintéticos

Exemplos de correcções, dossiers e citações usam frases inventadas. Não copiam texto de documentos reais nem pesos de modelos.
