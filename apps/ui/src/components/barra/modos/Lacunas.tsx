import { copy } from "../../../lib/copy";

export type LacunasProps = {
  valor: string;
  onChange: (v: string) => void;
  onEnviar: () => void;
};

export function Lacunas({ valor, onChange, onEnviar }: LacunasProps) {
  return (
    <textarea
      className="campo-escrita__input campo-escrita__textarea"
      rows={4}
      value={valor}
      placeholder={copy.bar.gaps_placeholder}
      aria-label={copy.bar.gaps_placeholder}
      data-modo="lacunas"
      onChange={(e) => onChange(e.target.value)}
      onKeyDown={(e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          onEnviar();
        }
      }}
    />
  );
}
