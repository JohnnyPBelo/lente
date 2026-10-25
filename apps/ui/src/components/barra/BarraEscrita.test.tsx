import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { reiniciarApiFalsa } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";

/** Teste que falha primeiro do PLN-14 (também coberto por REG-BAR-004). */
describe("BarraEscrita", () => {
  beforeEach(() => reiniciarApiFalsa());
  it("/ abre menu; setas; Enter em Correlacionar; Escape a Procurar", async () => {
    const u = userEvent.setup();
    render(<BarraEscrita />);
    await u.click(screen.getByLabelText(copy.bar.placeholder_search));
    await u.keyboard("/");
    expect(screen.getByRole("menu")).toBeInTheDocument();
    await u.keyboard("{ArrowDown}{Enter}");
    expect(screen.getByLabelText(copy.bar.correlate_a)).toBeInTheDocument();
    expect(screen.getByLabelText(copy.bar.correlate_b)).toBeInTheDocument();
    await u.keyboard("{Escape}");
    expect(screen.getByLabelText(copy.bar.placeholder_search)).toBeInTheDocument();
  });
});
