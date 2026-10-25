import { copy } from "../../lib/copy";
import { EstadoVazio } from "./EstadoVazio";

export function PaginaSemTexto() {
  return (
    <EstadoVazio
      estado="pagina-sem-texto"
      titulo={copy.vazios.pagina.titulo}
      corpo={copy.vazios.pagina.corpo}
    />
  );
}
