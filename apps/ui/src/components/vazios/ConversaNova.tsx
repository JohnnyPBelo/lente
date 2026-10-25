import { copy } from "../../lib/copy";
import { EstadoVazio } from "./EstadoVazio";

export function ConversaNova() {
  return (
    <EstadoVazio
      estado="conversa-nova"
      titulo={copy.vazios.conversa.titulo}
      corpo={copy.vazios.conversa.corpo}
    />
  );
}
