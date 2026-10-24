# Copy de interface (português de Portugal)

Origem: strings nomeadas ou implicadas em `docs/origem/plano.md` e nos fluxos desta pasta. A UI usa **estas** formulações (ou equivalentes mínimos sem anglicismos).

Convenção: português de Portugal (`ficheiro`, `seleccionar`, `correções`, `página`).

---

## Modos (menu `+` / `/` e pastilhas)

| Chave | String |
| --- | --- |
| mode.search | Procurar |
| mode.correlate | Correlacionar |
| mode.confront | Confrontar |
| mode.alert | Alerta |
| mode.gaps | Lacunas |

---

## Lentes (pastilha)

| Chave | String |
| --- | --- |
| lens.investigate | Investigar |
| lens.assessment | Assessment |
| lens.accreditation | Acreditação |
| lens.verify | Verificar |

Nota: «Assessment» mantém-se como nome de lente de trabalho do plano; o resto da UI permanece em português.

---

## Barra de escrita — placeholders e rótulos

| Chave | String |
| --- | --- |
| bar.placeholder.search | Pergunta ou termo a procurar |
| bar.correlate.a | Conceito A |
| bar.correlate.b | Conceito B |
| bar.confront.a | Trecho A |
| bar.confront.b | Trecho B |
| bar.confront.choose | Escolher |
| bar.alert.placeholder | O que queres que eu vigie? |
| bar.gaps.placeholder | Uma linha por controlo, hipótese ou pergunta |
| bar.menu.hint | Escolhe um modo |
| bar.send | Enviar |

---

## Confrontar — leituras e UI

| Chave | String |
| --- | --- |
| confront.reading.agree | Concordam |
| confront.reading.contradict | Contradizem-se |
| confront.reading.different | Falam de assuntos diferentes |
| confront.score | Pontuação |
| reader.bubble.confront | Confrontar |
| confront.pick.dim | Escolhe uma citação ou um trecho fixado |

---

## Pastilhas e chrome curto

| Chave | String |
| --- | --- |
| pill.mode | (nome do modo activo) |
| pill.lens | (nome da lente activa) |
| chrome.new_chat | Nova conversa |
| chrome.rename | Renomear |
| chrome.delete | Apagar |
| chrome.minimize | Minimizar |
| chrome.close | Fechar |
| chrome.cancel | Cancelar |
| chrome.confirm | Confirmar |
| chrome.export_proof | Exportar prova |
| chrome.backup | Cópia de segurança |

---

## Barra lateral — aprendizagem e Alertas

| Chave | String |
| --- | --- |
| learn.export | Exportar correções |
| learn.import | Importar correções |
| learn.group | Aprendizagem |
| alerts.group | Alertas |
| alerts.toggle.on | Alerta ligado |
| alerts.toggle.off | Alerta desligado |
| alerts.limit | Atingiste o máximo de 10 alertas |
| conversations.group | Conversas |

---

## Exportar correções (aviso obrigatório)

O ecrã de exportação **diz** que os trechos saem da máquina:

| Chave | String |
| --- | --- |
| export.title | Exportar correções |
| export.warning | Os trechos exportados são texto dos teus documentos. Ao exportar, essas frases **saem desta máquina**. |
| export.confirm | Exportar mesmo assim |
| export.cancel | Não exportar |
| import.title | Importar correções |
| import.summary | {n} correções · lentes: {lenses} |
| import.sample | Exemplos de perguntas |
| import.confirm | Confirmar e treinar quando a máquina estiver livre |
| import.reject_model | Este ficheiro é de outro modelo base e foi recusado |
| import.duplicates | Pares repetidos entram uma vez |

---

## Feedback na mensagem

| Chave | String |
| --- | --- |
| feedback.hit | Acertou |
| feedback.fix | Corrigir |
| feedback.dismiss | Descartar |
| feedback.fix_later | Corrigir mais tarde |
| feedback.correct.hint | Abre o leitor e selecciona o trecho certo |

---

## Chat — citações e resposta

| Chave | String |
| --- | --- |
| chat.citation | [{n}] |
| chat.open_source | Abrir na página |
| chat.threshold | Limiar |
| chat.empty_above_threshold | Não há nada acima do limiar |
| chat.prose_filtered | Nenhuma frase passou a verificação; ficam os excertos |
| chat.dossier.close | Fechar dossier |
| chat.dossier.reopen | Reabrir dossier |
| chat.dossier.source_changed | A fonte mudou depois do fecho; a prova antiga mantém-se |

---

## Leitor

| Chave | String |
| --- | --- |
| reader.zoom_in | Ampliar |
| reader.zoom_out | Reduzir |
| reader.fit_width | Ajustar à largura |
| reader.fit_page | Ajustar à página |
| reader.goto_page | Ir para a página |
| reader.page_of | Página {current} de {total} |
| reader.find_in_doc | Procurar neste documento |
| reader.toc | Sumário |
| reader.copy | Copiar |
| reader.copy_citation | Copiar citação |
| reader.pin_excerpt | Fixar trecho |
| reader.next_mark | Marca seguinte |
| reader.prev_mark | Marca anterior |
| reader.minimize | Minimizar |

Formato sugerido ao copiar citação: `{ficheiro}, p. {página}: «{texto}»`.

---

## Estados vazios (os sete do plano)

| Estado | Título | Corpo |
| --- | --- | --- |
| Biblioteca sem ficheiros | Biblioteca vazia | Ainda não há ficheiros. Acrescenta documentos para poderes procurar com prova na página. |
| Modelo a descarregar | A descarregar o modelo | A app continua utilizável; a prosa completa precisa deste modelo. Se a licença bloquear o download, coloca o ficheiro em: {caminho}. |
| Prosa toda filtrada | Sem prosa verificada | Nenhuma frase passou as duas portas. Podes abrir os excertos e as miniaturas. |
| Página sem texto | Página sem texto | Não há texto útil nesta página. Se for um scan, confirma o OCR na indexação. |
| URL recusada | URL recusada | Este endereço não é aceite (privado ou bloqueado). |
| Conversa nova | Nova conversa | Escreve a primeira procura na barra em baixo. |
| Procura sem documentos | Sem documentos | Não há documentos acima do limiar para esta procura. |

---

## Lacunas — estados por linha

| Chave | String |
| --- | --- |
| gaps.found | Encontrado |
| gaps.weak | Fraco |
| gaps.absent | Ausente |

---

## Correlacionar — legendas de cor

| Chave | String |
| --- | --- |
| correlate.legend.a | Conceito A |
| correlate.legend.b | Conceito B |
| correlate.legend.relation | Relação |

---

## Biblioteca e ingestão (chrome adjacente)

| Chave | String |
| --- | --- |
| lib.title | Biblioteca |
| lib.add | Acrescentar ficheiros |
| lib.outdated | Desactualizado |
| lib.tags | Etiquetas |
| lib.filter_type | Tipo de documento |
| ingest.refuse_url | URL recusada |

---

## Acessibilidade / motion

| Chave | String |
| --- | --- |
| a11y.fan | Leque de documentos |
| a11y.reader | Leitor de documento |
| a11y.sidebar | Barra lateral |
| a11y.write_bar | Barra de escrita |
| a11y.mode_menu | Menu de modos |

Sem copy separada para reduced motion: o comportamento muda; os rótulos mantêm-se.
