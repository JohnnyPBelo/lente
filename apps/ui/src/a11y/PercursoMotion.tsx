/**
 * Harness do percurso mensagem → leque → leitor → recolher.
 * Não substitui os componentes PLN-15; só prova reduced-motion (REG-A11-001).
 */

import { useState } from "react";
import { copy } from "../lib/copy";
import {
  duracaoMotionMs,
  prefersReducedMotion,
  proximaFase,
  type FasePercurso,
} from "./focos";

export type PercursoMotionProps = {
  reducedMotion?: boolean;
};

export function PercursoMotion({ reducedMotion }: PercursoMotionProps) {
  const reduzir =
    reducedMotion ??
    prefersReducedMotion(
      typeof window !== "undefined"
        ? window.matchMedia("(prefers-reduced-motion: reduce)")
        : undefined,
    );
  const duracao = duracaoMotionMs(reduzir);
  const [fase, setFase] = useState<FasePercurso>("mensagem");

  return (
    <div
      className="percurso-motion"
      data-reduced-motion={reduzir ? "reduce" : "no-preference"}
      data-fase={fase}
      style={{ ["--lente-motion-ms" as string]: `${duracao}ms` }}
    >
      <article
        className="percurso-motion__mensagem"
        data-testid="fase-mensagem"
        style={{ transitionDuration: `${duracao}ms` }}
      >
        Mensagem
      </article>

      <div
        role="region"
        aria-label={copy.a11y.fan}
        className="percurso-motion__leque"
        data-testid="fase-leque"
        data-slot="leque"
        style={{ transitionDuration: `${duracao}ms` }}
      >
        Leque
      </div>

      <div
        role="region"
        aria-label={copy.a11y.reader}
        className="percurso-motion__leitor"
        data-testid="fase-leitor"
        data-slot="leitor"
        style={{ transitionDuration: `${duracao}ms` }}
      >
        Leitor
        <button
          type="button"
          onClick={() => setFase("recolher")}
          aria-label={copy.chrome.minimize}
        >
          {copy.chrome.minimize}
        </button>
      </div>

      <button
        type="button"
        data-testid="avancar-fase"
        onClick={() => setFase((f) => proximaFase(f))}
      >
        Avançar
      </button>
    </div>
  );
}
