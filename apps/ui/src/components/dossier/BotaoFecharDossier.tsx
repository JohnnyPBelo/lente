/**
 * Botão explícito «Fechar dossier» — nunca automático por mensagem.
 * Copy: docs/interface/copy.md → chat.dossier.close
 */

import { copy } from "../../lib/copy";

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
      {copy.chat.dossier.close}
    </button>
  );
}
