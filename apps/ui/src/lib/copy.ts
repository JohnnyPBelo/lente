/** Strings visíveis — espelho de docs/interface/copy.md. Não inventar frases. */
export const copy = {
  chrome: {
    new_chat: "Nova conversa",
    rename: "Renomear",
    delete: "Apagar",
    minimize: "Minimizar",
    close: "Fechar",
    cancel: "Cancelar",
    confirm: "Confirmar",
    backup: "Cópia de segurança",
  },
  conversations: {
    group: "Conversas",
  },
  feedback: {
    hit: "Acertou",
    fix: "Corrigir",
    dismiss: "Descartar",
    fix_later: "Corrigir mais tarde",
  },
  learn: {
    export: "Exportar correções",
    import: "Importar correções",
    group: "Aprendizagem",
  },
  alerts: {
    group: "Alertas",
    toggle_on: "Alerta ligado",
    toggle_off: "Alerta desligado",
    limit: "Atingiste o máximo de 10 alertas",
  },
  mode: {
    search: "Procurar",
    correlate: "Correlacionar",
    confront: "Confrontar",
    alert: "Alerta",
    gaps: "Lacunas",
  },
  lens: {
    investigate: "Investigar",
    assessment: "Assessment",
    accreditation: "Acreditação",
    verify: "Verificar",
  },
  bar: {
    placeholder_search: "Pergunta ou termo a procurar",
    correlate_a: "Conceito A",
    correlate_b: "Conceito B",
    confront_a: "Trecho A",
    confront_b: "Trecho B",
    confront_choose: "Escolher",
    alert_placeholder: "O que queres que eu vigie?",
    gaps_placeholder: "Uma linha por controlo, hipótese ou pergunta",
    send: "Enviar",
    menu_hint: "Escolhe um modo",
    threshold: "Limiar",
    threshold_raw: "Limiar bruto",
    threshold_uncalibrated: "sem calibração",
  },
  confront: {
    reading_agree: "Concordam",
    reading_contradict: "Contradizem-se",
    reading_different: "Falam de assuntos diferentes",
    score: "Pontuação",
    pick_dim: "Escolhe uma citação ou um trecho fixado",
  },
  gaps: {
    found: "Encontrado",
    weak: "Fraco",
    absent: "Ausente",
  },
  correlate: {
    legend_a: "Conceito A",
    legend_b: "Conceito B",
    legend_relation: "Relação",
  },
  export: {
    title: "Exportar correções",
    warning:
      "Os trechos exportados são texto dos teus documentos. Ao exportar, essas frases **saem desta máquina**.",
    confirm: "Exportar mesmo assim",
    cancel: "Não exportar",
  },
  import: {
    title: "Importar correções",
    summary: "{n} correções · lentes: {lenses}",
    sample: "Exemplos de perguntas",
    confirm: "Confirmar e treinar quando a máquina estiver livre",
    reject_model: "Este ficheiro é de outro modelo base e foi recusado",
    duplicates: "Pares repetidos entram uma vez",
  },
  chat: {
    citation: "[{n}]",
    empty_title: "Nova conversa",
    empty_body: "Escreve a primeira procura na barra em baixo.",
    threshold: "Limiar",
    threshold_raw: "Limiar bruto",
    threshold_uncalibrated: "sem calibração",
    open_source: "Abrir na página",
    dossier: {
      close: "Fechar dossier",
      reopen: "Reabrir dossier",
      source_changed: "A fonte mudou depois do fecho; a prova antiga mantém-se",
    },
  },
  lib: {
    title: "Biblioteca",
    add: "Acrescentar ficheiros",
    add_url: "Acrescentar URL",
    url_placeholder: "https://…",
    outdated: "Desactualizado",
    tags: "Etiquetas",
    filter_type: "Tipo de documento",
  },
  vazios: {
    biblioteca: {
      titulo: "Biblioteca vazia",
      corpo:
        "Ainda não há ficheiros. Acrescenta documentos para poderes procurar com prova na página.",
    },
    modelo: {
      titulo: "A descarregar o modelo",
      corpo:
        "A app continua utilizável; a prosa completa precisa deste modelo. Se a licença bloquear o download, coloca o ficheiro em: {caminho}.",
    },
    prosa: {
      titulo: "Sem prosa verificada",
      corpo:
        "Nenhuma frase passou as duas portas. Podes abrir os excertos e as miniaturas.",
    },
    pagina: {
      titulo: "Página sem texto",
      corpo:
        "Não há texto útil nesta página. Se for um scan, confirma o OCR na indexação.",
    },
    url: {
      titulo: "URL recusada",
      corpo: "Este endereço não é aceite (privado ou bloqueado).",
    },
    conversa: {
      titulo: "Nova conversa",
      corpo: "Escreve a primeira procura na barra em baixo.",
    },
    procura: {
      titulo: "Sem documentos",
      corpo: "Não há documentos acima do limiar para esta procura.",
    },
  },
  reader: {
    zoom_in: "Ampliar",
    zoom_out: "Reduzir",
    fit_width: "Ajustar à largura",
    fit_page: "Ajustar à página",
    goto_page: "Ir para a página",
    page_of: "Página {current} de {total}",
    find_in_doc: "Procurar neste documento",
    toc: "Sumário",
    copy: "Copiar",
    copy_citation: "Copiar citação",
    pin_excerpt: "Fixar trecho",
    next_mark: "Marca seguinte",
    prev_mark: "Marca anterior",
    minimize: "Minimizar",
    bubble_confront: "Confrontar",
  },
  a11y: {
    sidebar: "Barra lateral",
    write_bar: "Barra de escrita",
    fan: "Leque de documentos",
    reader: "Leitor de documento",
    mode_menu: "Menu de modos",
    onboarding: "Introdução à Lente",
  },
  onboarding: {
    title: "Como usar a Lente",
    ja_vi: "Já vi",
    seguinte: "Seguinte",
    anterior: "Anterior",
    passo_de: "Passo {actual} de {total}",
    passos: {
      procura: {
        titulo: "Procurar",
        corpo:
          "Na barra em baixo, escreve a pergunta e Enter envia. A resposta cita trechos com prova na página; se nada passar o limiar, vês o aviso sem documentos inventados.",
      },
      correlacionar: {
        titulo: "Correlacionar",
        corpo:
          "No menu + ou /, escolhe Correlacionar. Dois campos — Conceito A e Conceito B — e o fio mostra a relação com três cores e o leque de documentos.",
      },
      confrontar: {
        titulo: "Confrontar",
        corpo:
          "Dois lugares (Trecho A e B). Escolher pega numa citação ou trecho fixado; sem citações, podes colar texto. O juiz devolve: concordam, contradizem-se, ou falam de assuntos diferentes.",
      },
      alerta: {
        titulo: "Alerta",
        corpo:
          "Um campo: «O que queres que eu vigie?». Até dez alertas. Documentos novos indexados são revistos; os antigos não. O interruptor fica no fio do alerta.",
      },
      lacunas: {
        titulo: "Lacunas",
        corpo:
          "Várias linhas — uma por controlo, hipótese ou pergunta. Sai uma lista encontrado / fraco / ausente, com citação para abrir o leitor. Sem o E2B e sem repetição sozinha.",
      },
      biblioteca: {
        titulo: "Biblioteca e ingestão",
        corpo:
          "O botão Biblioteca acrescenta ficheiros ou URL. Texto, Markdown, docx, PDF, imagem (OCR) e URL pública. Ficheiros que mudam no disco ficam marcados como desactualizados.",
      },
      leque: {
        titulo: "Leque e leitor",
        corpo:
          "Uma miniatura por documento. Um só: o clique abre o leitor. Vários: o leque escolhe qual cresce até ao leitor. Minimizar ou Escape recolhe; prefers-reduced-motion encurta o movimento.",
      },
      feedback: {
        titulo: "Feedback e aprendizagem",
        corpo:
          "Na mensagem: Acertou, Corrigir, Descartar — só treina o juiz. Exportar e Importar correções ficam no topo da barra lateral (Aprendizagem), não no menu +.",
      },
      dossier: {
        titulo: "Dossier",
        corpo:
          "Fechar dossier grava uma fotografia da prova no SQLite. Reabrir lê essa fotografia; se a fonte mudou depois do fecho, a app avisa e a prova antiga mantém-se.",
      },
      alertas: {
        titulo: "Alertas na barra lateral",
        corpo:
          "Por baixo das conversas, o grupo Alertas lista o que criaste. Cada um abre o seu fio; o interruptor liga ou desliga a vigilância.",
      },
      backup: {
        titulo: "Cópia de segurança",
        corpo:
          "Na barra lateral, Cópia de segurança compacta a pasta data/ num zip no sítio que escolheres. Sem nuvem nem contas.",
      },
      modelos: {
        titulo: "Modelos",
        corpo:
          "Embedding e juiz devem estar prontos para procura com highlights. Sem o escritor (E2B), a app continua com excertos e miniaturas. Se faltarem pesos, a orientação indica o caminho em models/.",
        pronto: "Pronto",
        ausente: "Ausente ou a descarregar",
        embedding: "Embedding",
        juiz: "Juiz",
        escritor: "Escritor (E2B)",
      },
    },
  },
} as const;

/** Entradas do menu + / / — sem exportar/importar correções (REQ-BAR-012). */
export const entradasMenuMais = [
  copy.mode.search,
  copy.mode.correlate,
  copy.mode.confront,
  copy.mode.alert,
  copy.mode.gaps,
] as const;
