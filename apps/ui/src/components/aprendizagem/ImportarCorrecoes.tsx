import { useMemo, useState } from "react";
import { copy } from "../../lib/copy";

export type PreviaImportacao = {
  contagem: number;
  lentes: string[];
  amostra_perguntas: string[];
  duplicados_ignorados?: number;
  modelo_base_ok: boolean;
};

export type ImportarCorrecoesProps = {
  previa?: PreviaImportacao | null;
  onConfirmar?: () => void | Promise<void>;
  onCancelar?: () => void;
};

function resumo(previa: PreviaImportacao): string {
  return copy.import.summary
    .replace("{n}", String(previa.contagem))
    .replace("{lenses}", previa.lentes.join(", "));
}

/**
 * Pré-visualização + confirmação obrigatória antes de treinar (REQ-FBK-014).
 */
export function ImportarCorrecoes({
  previa = null,
  onConfirmar,
  onCancelar,
}: ImportarCorrecoesProps) {
  const [aConfirmar, setAConfirmar] = useState(false);
  const textoResumo = useMemo(
    () => (previa ? resumo(previa) : null),
    [previa],
  );

  async function confirmar() {
    if (!previa?.modelo_base_ok) {
      return;
    }
    setAConfirmar(true);
    try {
      await onConfirmar?.();
    } finally {
      setAConfirmar(false);
    }
  }

  return (
    <section
      className="importar-correcoes"
      aria-labelledby="importar-correcoes-titulo"
    >
      <h2 id="importar-correcoes-titulo">{copy.import.title}</h2>
      {previa && !previa.modelo_base_ok ? (
        <p role="alert">{copy.import.reject_model}</p>
      ) : null}
      {previa && previa.modelo_base_ok ? (
        <>
          <p data-testid="import-summary">{textoResumo}</p>
          <p>{copy.import.duplicates}</p>
          <h3>{copy.import.sample}</h3>
          <ul>
            {previa.amostra_perguntas.map((pergunta) => (
              <li key={pergunta}>{pergunta}</li>
            ))}
          </ul>
          <div className="importar-correcoes__acoes">
            <button
              type="button"
              onClick={() => void confirmar()}
              disabled={aConfirmar}
            >
              {copy.import.confirm}
            </button>
            <button type="button" onClick={() => onCancelar?.()}>
              {copy.chrome.cancel}
            </button>
          </div>
        </>
      ) : null}
    </section>
  );
}
