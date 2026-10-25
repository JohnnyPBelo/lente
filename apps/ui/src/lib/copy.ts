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
  learn: {
    lens: {
    investigate: "Investigar",
    assessment: "Assessment",
    accreditation: "Acreditação",
    verify: "Verificar",
  },
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
    empty_title: "Nova conversa",
    empty_body: "Escreve a primeira procura na barra em baixo.",
    threshold: "Limiar",
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
  a11y: {
    sidebar: "Barra lateral",
    write_bar: "Barra de escrita",
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
