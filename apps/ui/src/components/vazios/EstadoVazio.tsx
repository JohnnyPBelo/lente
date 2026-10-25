/** Contentor partilhado dos sete estados vazios — só hierarquia e copy. */

import type { ReactNode } from "react";

export type EstadoVazioProps = {
  titulo: string;
  corpo: string;
  /** Identificador estável para testes (`data-estado`). */
  estado: string;
  children?: ReactNode;
};

export function EstadoVazio({
  titulo,
  corpo,
  estado,
  children,
}: EstadoVazioProps) {
  return (
    <section
      className="estado-vazio"
      data-estado={estado}
      aria-labelledby={`vazio-${estado}-titulo`}
    >
      <h2 id={`vazio-${estado}-titulo`}>{titulo}</h2>
      <p>{corpo}</p>
      {children}
    </section>
  );
}
