import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { copy } from "../lib/copy";
import { DURACAO_MOTION_MS, DURACAO_REDUZIDA_MS, duracaoMotionMs } from "./focos";
import { PercursoMotion } from "./PercursoMotion";

describe("REG-A11-001", () => {
  it("com prefers-reduced-motion encurta animações sem remover leque/leitor", async () => {
    const utilizador = userEvent.setup();
    render(<PercursoMotion reducedMotion />);

    const raiz = document.querySelector(".percurso-motion");
    expect(raiz).toHaveAttribute("data-reduced-motion", "reduce");
    expect(duracaoMotionMs(true)).toBe(DURACAO_REDUZIDA_MS);
    expect(DURACAO_REDUZIDA_MS).toBeLessThan(DURACAO_MOTION_MS);

    const leque = screen.getByRole("region", { name: copy.a11y.fan });
    const leitor = screen.getByRole("region", { name: copy.a11y.reader });
    expect(leque).toBeInTheDocument();
    expect(leitor).toBeInTheDocument();

    expect(leque).toHaveStyle({ transitionDuration: `${DURACAO_REDUZIDA_MS}ms` });
    expect(leitor).toHaveStyle({ transitionDuration: `${DURACAO_REDUZIDA_MS}ms` });

    await utilizador.click(screen.getByTestId("avancar-fase"));
    expect(raiz).toHaveAttribute("data-fase", "leque");
    await utilizador.click(screen.getByTestId("avancar-fase"));
    expect(raiz).toHaveAttribute("data-fase", "leitor");
    await utilizador.click(screen.getByRole("button", { name: copy.chrome.minimize }));
    expect(raiz).toHaveAttribute("data-fase", "recolher");

    // Continuam utilizáveis após o percurso.
    expect(leque).toBeVisible();
    expect(leitor).toBeVisible();
  });

  it("sem reduce mantém duração normal e superfícies", () => {
    render(<PercursoMotion reducedMotion={false} />);
    const leque = screen.getByRole("region", { name: copy.a11y.fan });
    expect(leque).toHaveStyle({ transitionDuration: `${DURACAO_MOTION_MS}ms` });
  });
});
