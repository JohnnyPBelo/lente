import { copy } from "../../lib/copy";
import { EstadoVazio } from "./EstadoVazio";

export type BibliotecaVaziaProps = {
  onAcrescentar?: () => void;
};

export function BibliotecaVazia({ onAcrescentar }: BibliotecaVaziaProps) {
  return (
    <EstadoVazio
      estado="biblioteca-vazia"
      titulo={copy.vazios.biblioteca.titulo}
      corpo={copy.vazios.biblioteca.corpo}
    >
      {onAcrescentar ? (
        <button type="button" className="botao-primario" onClick={onAcrescentar}>
          {copy.lib.add}
        </button>
      ) : null}
    </EstadoVazio>
  );
}
