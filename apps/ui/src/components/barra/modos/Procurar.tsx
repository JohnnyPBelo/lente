import { copy } from "../../../lib/copy";

export type ProcurarProps = {
  valor: string;
  onChange: (v: string) => void;
  onEnviar: () => void;
  inputRef?: React.Ref<HTMLInputElement>;
};

export function Procurar({ valor, onChange, onEnviar, inputRef }: ProcurarProps) {
  return (
    <input
      ref={inputRef}
      className="campo-escrita__input"
      type="text"
      value={valor}
      placeholder={copy.bar.placeholder_search}
      aria-label={copy.bar.placeholder_search}
      autoComplete="off"
      onChange={(e) => onChange(e.target.value)}
      onKeyDown={(e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          onEnviar();
        }
      }}
    />
  );
}
