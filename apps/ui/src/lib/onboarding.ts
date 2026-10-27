/** Persistência do primeiro uso — local, sem contas. */

export const CHAVE_ONBOARDING_JA_VI = "lente.onboarding.ja_vi";

export const IDS_PASSOS_ONBOARDING = [
  "procura",
  "correlacionar",
  "confrontar",
  "alerta",
  "lacunas",
  "biblioteca",
  "leque",
  "feedback",
  "dossier",
  "alertas",
  "backup",
  "modelos",
] as const;

export type IdPassoOnboarding = (typeof IDS_PASSOS_ONBOARDING)[number];

export function lerJaVi(
  armazenamento: Pick<Storage, "getItem"> | null | undefined = undefined,
): boolean {
  const store =
    armazenamento ??
    (typeof localStorage !== "undefined" ? localStorage : null);
  if (!store) return false;
  try {
    return store.getItem(CHAVE_ONBOARDING_JA_VI) === "1";
  } catch {
    return false;
  }
}

export function gravarJaVi(
  armazenamento: Pick<Storage, "setItem"> | null | undefined = undefined,
): void {
  const store =
    armazenamento ??
    (typeof localStorage !== "undefined" ? localStorage : null);
  if (!store) return;
  try {
    store.setItem(CHAVE_ONBOARDING_JA_VI, "1");
  } catch {
    /* quota / modo privado — a UI fecha na mesma */
  }
}

export function limparJaVi(
  armazenamento: Pick<Storage, "removeItem"> | null | undefined = undefined,
): void {
  const store =
    armazenamento ??
    (typeof localStorage !== "undefined" ? localStorage : null);
  if (!store) return;
  try {
    store.removeItem(CHAVE_ONBOARDING_JA_VI);
  } catch {
    /* ignorar */
  }
}

/** `?onboarding=1` força o diálogo (útil para rever a introdução). */
export function forcarOnboardingNaUrl(
  pesquisa: string | null | undefined = undefined,
): boolean {
  const q =
    pesquisa ??
    (typeof window !== "undefined" ? window.location.search : "");
  if (!q) return false;
  try {
    return new URLSearchParams(q).get("onboarding") === "1";
  } catch {
    return false;
  }
}

export function deveMostrarOnboarding(opcoes?: {
  armazenamento?: Pick<Storage, "getItem"> | null;
  pesquisa?: string | null;
}): boolean {
  if (forcarOnboardingNaUrl(opcoes?.pesquisa)) return true;
  return !lerJaVi(opcoes?.armazenamento);
}
