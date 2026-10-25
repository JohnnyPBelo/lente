import { copy } from "../../../lib/copy";

export type TrechoBarra = {
  texto: string;
  documento_id?: string;
  pagina?: number;
};

export type ConfrontarProps = {
  trechoA: TrechoBarra;
  trechoB: TrechoBarra;
  aEscolher: "a" | "b" | null;
  onChangeA: (t: TrechoBarra) => void;
  onChangeB: (t: TrechoBarra) => void;
  onEscolher: (lugar: "a" | "b") => void;
  onEnviar: () => void;
};

export function Confrontar({
  trechoA,
  trechoB,
  aEscolher,
  onChangeA,
  onChangeB,
  onEscolher,
  onEnviar,
}: ConfrontarProps) {
  function tecla(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onEnviar();
    }
  }
  return (
    <div
      className="barra-dois-campos"
      data-modo="confrontar"
      data-escolher={aEscolher ?? ""}
    >
      <div className="confrontar-lugar">
        <label>
          <span className="sr-only">{copy.bar.confront_a}</span>
          <textarea
            className="campo-escrita__input"
            rows={2}
            value={trechoA.texto}
            placeholder={copy.bar.confront_a}
            aria-label={copy.bar.confront_a}
            onChange={(e) => onChangeA({ ...trechoA, texto: e.target.value })}
            onKeyDown={tecla}
          />
        </label>
        <button
          type="button"
          className="botao-fantasma"
          aria-pressed={aEscolher === "a"}
          onClick={() => onEscolher("a")}
        >
          {copy.bar.confront_choose}
        </button>
      </div>
      <div className="confrontar-lugar">
        <label>
          <span className="sr-only">{copy.bar.confront_b}</span>
          <textarea
            className="campo-escrita__input"
            rows={2}
            value={trechoB.texto}
            placeholder={copy.bar.confront_b}
            aria-label={copy.bar.confront_b}
            onChange={(e) => onChangeB({ ...trechoB, texto: e.target.value })}
            onKeyDown={tecla}
          />
        </label>
        <button
          type="button"
          className="botao-fantasma"
          aria-pressed={aEscolher === "b"}
          onClick={() => onEscolher("b")}
        >
          {copy.bar.confront_choose}
        </button>
      </div>
    </div>
  );
}
