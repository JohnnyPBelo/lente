/** Mapeamento lente → prefixo EmbeddingGemma e instrução E2B (ADR-009). */

export type LenteId =
  | "investigar"
  | "assessment"
  | "acreditacao"
  | "verificar";

export type ModoId =
  | "procurar"
  | "correlacionar"
  | "confrontar"
  | "alerta"
  | "lacunas";

export const LENTES: readonly LenteId[] = [
  "investigar",
  "assessment",
  "acreditacao",
  "verificar",
] as const;

export const MODOS: readonly ModoId[] = [
  "procurar",
  "correlacionar",
  "confrontar",
  "alerta",
  "lacunas",
] as const;

/** Prefixo de query EmbeddingGemma 2 para a lente/modo. */
export function prefixoEmbedding(
  lente: LenteId,
  modo: ModoId,
  query: string,
): string {
  if (modo === "confrontar") {
    return `task: search result | query: ${query}`;
  }
  if (modo === "procurar" && lente === "investigar") {
    // Procurar em repouso com lente investigar usa QA; pesquisa curta sem lente
    // especializada também pode usar search result — a pastilha activa define.
  }
  switch (lente) {
    case "investigar":
    case "acreditacao":
      return `task: question answering | query: ${query}`;
    case "verificar":
    case "assessment":
      return `task: fact checking | query: ${query}`;
    default:
      return `task: search result | query: ${query}`;
  }
}

/** Prefixo de procura curta (repouso sem lente especializada). */
export function prefixoProcuraCurta(query: string): string {
  return `task: search result | query: ${query}`;
}

export const instrucaoProsa: Record<LenteId, string> = {
  investigar: `Responde em português de Portugal. Usa só os trechos numerados desta procura.
Cada frase afirmativa termina com a citação [n] do trecho que a sustenta.
Não inventes controlos, datas nem cláusulas que não estejam nos trechos.
Prefere frases curtas e ligadas à prova na página.`,
  assessment: `Responde em português de Portugal no registo de assessment: o que o texto afirma, o que falta, e o risco residual só se os trechos o permitirem.
Cada afirmação termina com [n]. Sem [n], não escrevas a frase.
Não emits parecer jurídico nem receita de ataque; resume evidência citada.`,
  acreditacao: `Responde em português de Portugal no registo de acreditação: requisitos, evidências e lacunas só com base nos trechos.
Cada frase de conformidade ou não conformidade termina com [n].
Não completes requisitos com conhecimento geral fora dos trechos.`,
  verificar: `Responde em português de Portugal. Trata a pergunta como verificação factual contra os trechos.
Marca o que está suportado, o que está contradito e o que está ausente; cada afirmação com [n].
Não suavizes contradições; cita o trecho.`,
};
