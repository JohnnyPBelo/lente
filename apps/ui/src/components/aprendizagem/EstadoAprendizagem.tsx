import { useState } from "react";
import { copy } from "../../lib/copy";
import { ExportarCorrecoes } from "./ExportarCorrecoes";
import {
  ImportarCorrecoes,
  type PreviaImportacao,
} from "./ImportarCorrecoes";

export type EstadoAprendizagemProps = {
  previaImportacao?: PreviaImportacao | null;
  onExportar?: () => void | Promise<void>;
  onConfirmarImportacao?: () => void | Promise<void>;
};

/**
 * Estado da aprendizagem no topo da barra lateral: Exportar / Importar
 * (REQ-FBK-017). Não vive no menu + da barra de escrita.
 */
export function EstadoAprendizagem({
  previaImportacao = null,
  onExportar,
  onConfirmarImportacao,
}: EstadoAprendizagemProps) {
  const [ecra, setEcra] = useState<"lista" | "exportar" | "importar">("lista");

  return (
    <div className="barra-lateral__aprendizagem" data-testid="estado-aprendizagem">
      <p className="barra-lateral__grupo">{copy.learn.group}</p>
      {ecra === "lista" ? (
        <div className="barra-lateral__acoes-aprendizagem">
          <button type="button" onClick={() => setEcra("exportar")}>
            {copy.learn.export}
          </button>
          <button type="button" onClick={() => setEcra("importar")}>
            {copy.learn.import}
          </button>
        </div>
      ) : null}
      {ecra === "exportar" ? (
        <ExportarCorrecoes
          onConfirmar={onExportar}
          onCancelar={() => setEcra("lista")}
        />
      ) : null}
      {ecra === "importar" ? (
        <ImportarCorrecoes
          previa={previaImportacao}
          onConfirmar={onConfirmarImportacao}
          onCancelar={() => setEcra("lista")}
        />
      ) : null}
    </div>
  );
}
