import { useState, type FormEvent } from "react";
import { copy } from "../../lib/copy";

export type CampoEscritaBaseProps = {
  onEnviar?: (texto: string) => void;
  disabled?: boolean;
};

/**
 * Campo de escrita + botão `+` stub (menu de modos = PLN-14).
 */
export function CampoEscritaBase({
  onEnviar,
  disabled = false,
}: CampoEscritaBaseProps) {
  const [texto, setTexto] = useState("");

  function submeter(evento: FormEvent) {
    evento.preventDefault();
    const valor = texto.trim();
    if (!valor || disabled) {
      return;
    }
    onEnviar?.(valor);
    setTexto("");
  }

  return (
    <form
      className="campo-escrita vidro"
      aria-label={copy.a11y.write_bar}
      onSubmit={submeter}
    >
      <button
        type="button"
        className="botao-icone campo-escrita__mais"
        aria-label={copy.bar.menu_hint}
        title={copy.bar.menu_hint}
        disabled
      >
        +
      </button>
      <label className="sr-only" htmlFor="campo-escrita-input">
        {copy.bar.placeholder_search}
      </label>
      <input
        id="campo-escrita-input"
        className="campo-escrita__input"
        type="text"
        value={texto}
        disabled={disabled}
        placeholder={copy.bar.placeholder_search}
        onChange={(evento) => setTexto(evento.target.value)}
        autoComplete="off"
      />
      <button
        type="submit"
        className="botao-primario"
        disabled={disabled || !texto.trim()}
      >
        {copy.bar.send}
      </button>
    </form>
  );
}
