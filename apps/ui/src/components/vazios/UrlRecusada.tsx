import { copy } from "../../lib/copy";
import { EstadoVazio } from "./EstadoVazio";

export function UrlRecusada() {
  return (
    <EstadoVazio
      estado="url-recusada"
      titulo={copy.vazios.url.titulo}
      corpo={copy.vazios.url.corpo}
    />
  );
}
