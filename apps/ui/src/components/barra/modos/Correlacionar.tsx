import { copy } from "../../../lib/copy";

export type CorrelacionarProps = {
  conceitoA: string;
  conceitoB: string;
  onChangeA: (v: string) => void;
  onChangeB: (v: string) => void;
  onEnviar: () => void;
};

export function Correlacionar({
  conceitoA,
  conceitoB,
  onChangeA,
  onChangeB,
  onEnviar,
}: CorrelacionarProps) {
  function tecla(e: React.KeyboardEvent) {
    if (e.key === "Enter") {
      e.preventDefault();
      onEnviar();
    }
  }
  return (
    <div className="barra-dois-campos" data-modo="correlacionar">
      <label>
        <span className="sr-only">{copy.bar.correlate_a}</span>
        <input
          className="campo-escrita__input"
          type="text"
          value={conceitoA}
          placeholder={copy.bar.correlate_a}
          aria-label={copy.bar.correlate_a}
          onChange={(e) => onChangeA(e.target.value)}
          onKeyDown={tecla}
        />
      </label>
      <label>
        <span className="sr-only">{copy.bar.correlate_b}</span>
        <input
          className="campo-escrita__input"
          type="text"
          value={conceitoB}
          placeholder={copy.bar.correlate_b}
          aria-label={copy.bar.correlate_b}
          onChange={(e) => onChangeB(e.target.value)}
          onKeyDown={tecla}
        />
      </label>
    </div>
  );
}
