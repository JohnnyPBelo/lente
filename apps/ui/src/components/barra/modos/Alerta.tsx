import { copy } from "../../../lib/copy";

export type AlertaProps = {
  valor: string;
  onChange: (v: string) => void;
  onEnviar: () => void;
  erroLimite?: string | null;
};

export function Alerta({ valor, onChange, onEnviar, erroLimite }: AlertaProps) {
  return (
    <div className="modo-alerta" data-modo="alerta">
      <input
        className="campo-escrita__input"
        type="text"
        value={valor}
        placeholder={copy.bar.alert_placeholder}
        aria-label={copy.bar.alert_placeholder}
        autoComplete="off"
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            onEnviar();
          }
        }}
      />
      {erroLimite ? (
        <p className="barra-erro" role="alert">
          {erroLimite}
        </p>
      ) : null}
    </div>
  );
}
