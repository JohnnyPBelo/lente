import { copy } from "../../lib/copy";
import { EstadoVazio } from "./EstadoVazio";

export function ProcuraSemDocumentos() {
  return (
    <EstadoVazio
      estado="procura-sem-documentos"
      titulo={copy.vazios.procura.titulo}
      corpo={copy.vazios.procura.corpo}
    >
      {/* Sem miniaturas a fingir resultados */}
      <div data-testid="miniaturas-falsas" hidden />
    </EstadoVazio>
  );
}
