/**
 * Botão explícito «Fechar dossier» — nunca automático por mensagem.
 * Copy: docs/interface/copy.md → chat.dossier.close
 */

export const COPY_DOSSIER_CLOSE = "Fechar dossier";

export type BotaoFecharDossierProps = {
  onFechar: () => void | Promise<void>;
  disabled?: boolean;
};

export function BotaoFecharDossier({
  onFechar,
  disabled = false,
}: BotaoFecharDossierProps) {
  return (
    <button
      type="button"
      className="dossier-fechar"
      disabled={disabled}
      onClick={() => {
        void onFechar();
      }}
    >
      {COPY_DOSSIER_CLOSE}
    </button>
  );
}
