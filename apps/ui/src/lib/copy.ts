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
