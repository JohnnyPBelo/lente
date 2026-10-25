import { copy } from "../../lib/copy";
import { EstadoVazio } from "./EstadoVazio";

export type ModeloADescarregarProps = {
  /** Caminho em models/ onde pôr o ficheiro se a licença bloquear. */
  caminho: string;
};

export function ModeloADescarregar({ caminho }: ModeloADescarregarProps) {
  const corpo = copy.vazios.modelo.corpo.replace("{caminho}", caminho);
  return (
    <EstadoVazio
      estado="modelo-a-descarregar"
      titulo={copy.vazios.modelo.titulo}
      corpo={corpo}
    />
  );
}
