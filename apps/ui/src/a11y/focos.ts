/**
 * Helpers de foco e motion (REQ-A11-001).
 * O leque/leitor reais são PLN-15; aqui só o contrato de reduced-motion.
 */

export const DURACAO_MOTION_MS = 280;
export const DURACAO_REDUZIDA_MS = 1;

export type FasePercurso =
  | "mensagem"
  | "leque"
  | "leitor"
  | "recolher"
  | "repouso";

export function prefersReducedMotion(
  media: Pick<MediaQueryList, "matches"> | null | undefined = undefined,
): boolean {
  if (media != null) {
    return media.matches;
  }
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return false;
  }
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function duracaoMotionMs(reduzir: boolean): number {
  return reduzir ? DURACAO_REDUZIDA_MS : DURACAO_MOTION_MS;
}

/** Ordem de tab sugerida no chrome (checklist). */
export const ORDEM_FOCO_CHROME = [
  "barra-lateral",
  "area-chat",
  "barra-escrita",
  "leque",
  "leitor",
] as const;

export function proximaFase(actual: FasePercurso): FasePercurso {
  const ordem: FasePercurso[] = [
    "mensagem",
    "leque",
    "leitor",
    "recolher",
    "repouso",
  ];
  const i = ordem.indexOf(actual);
  if (i < 0 || i >= ordem.length - 1) {
    return "repouso";
  }
  return ordem[i + 1]!;
}
