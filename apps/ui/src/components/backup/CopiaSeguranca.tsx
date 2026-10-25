import { useState } from "react";
import { copy } from "../../lib/copy";

export type CopiaSegurancaProps = {
  /** Pedido local de zip; destino é caminho na máquina do utilizador. */
  onCopiar?: (destino: string) => Promise<void> | void;
};

/**
 * Acção de cópia de segurança — zip local de data/, sem nuvem.
 * Copy: chrome.backup.
 */
export function CopiaSeguranca({ onCopiar }: CopiaSegurancaProps) {
  const [destino, setDestino] = useState("");
  const [aCorrer, setACorrer] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  async function aoConfirmar() {
    const caminho = destino.trim();
    if (!caminho) {
      return;
    }
    setACorrer(true);
    setErro(null);
    try {
      await onCopiar?.(caminho);
    } catch (e) {
      setErro(e instanceof Error ? e.message : String(e));
    } finally {
      setACorrer(false);
    }
  }

  return (
    <div data-testid="copia-seguranca">
      <button
        type="button"
        disabled={aCorrer}
        onClick={() => void aoConfirmar()}
      >
        {copy.chrome.backup}
      </button>
      <label>
        {copy.chrome.backup}
        <input
          type="text"
          value={destino}
          onChange={(e) => setDestino(e.target.value)}
          placeholder="/caminho/escolhido/lente-data.zip"
          aria-label={copy.chrome.backup}
        />
      </label>
      {erro ? <p role="alert">{erro}</p> : null}
    </div>
  );
}
