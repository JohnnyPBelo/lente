import { copy } from "../../lib/copy";
import { EstadoVazio } from "./EstadoVazio";

export type ProsaFiltradaProps = {
  /** Excertos reais (não prosa fantasma). */
  excertos?: string[];
};

export function ProsaFiltrada({ excertos = [] }: ProsaFiltradaProps) {
  return (
    <EstadoVazio
      estado="prosa-filtrada"
      titulo={copy.vazios.prosa.titulo}
      corpo={copy.vazios.prosa.corpo}
    >
      {excertos.length > 0 ? (
        <ul data-testid="excertos-reais">
          {excertos.map((texto, i) => (
            <li key={i}>{texto}</li>
          ))}
        </ul>
      ) : null}
      {/* Proibido: prosa inventada / fantasma */}
      <div data-testid="prosa-fantasma" hidden />
    </EstadoVazio>
  );
}
