import { useState } from "react";
import { copy } from "../../lib/copy";

export type ExportarCorrecoesProps = {
  onConfirmar?: () => void | Promise<void>;
  onCancelar?: () => void;
};

/**
 * Ecrã de exportação: aviso obrigatório de que os trechos saem da máquina
 * (REQ-FBK-013 / export.warning).
 */
export function ExportarCorrecoes({
  onConfirmar,
  onCancelar,
}: ExportarCorrecoesProps) {
  const [aConfirmar, setAConfirmar] = useState(false);

  async function confirmar() {
    setAConfirmar(true);
    try {
      await onConfirmar?.();
    } finally {
      setAConfirmar(false);
    }
  }

  return (
    <section
      className="exportar-correcoes"
      aria-labelledby="exportar-correcoes-titulo"
    >
      <h2 id="exportar-correcoes-titulo">{copy.export.title}</h2>
      <p role="status" data-testid="export-warning">
        {copy.export.warning}
      </p>
      <div className="exportar-correcoes__acoes">
        <button type="button" onClick={() => void confirmar()} disabled={aConfirmar}>
          {copy.export.confirm}
        </button>
        <button type="button" onClick={() => onCancelar?.()}>
          {copy.export.cancel}
        </button>
      </div>
    </section>
  );
}
