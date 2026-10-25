import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { reiniciarApiFalsa } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";

describe("REG-BAR-007", () => {
  beforeEach(() => reiniciarApiFalsa());
  it("Correlacionar envia Conceito A e B", async () => {
    const u = userEvent.setup();
    const onResultado = vi.fn();
    render(<BarraEscrita onResultado={onResultado} />);
    await u.click(screen.getByRole("button", { name: copy.bar.menu_hint }));
    await u.click(screen.getByRole("menuitem", { name: copy.mode.correlate }));
    expect(screen.getByLabelText(copy.bar.correlate_a)).toBeInTheDocument();
    expect(screen.getByLabelText(copy.bar.correlate_b)).toBeInTheDocument();
    await u.type(screen.getByLabelText(copy.bar.correlate_a), "acessos");
    await u.type(screen.getByLabelText(copy.bar.correlate_b), "auditoria{Enter}");
    expect(onResultado).toHaveBeenCalledWith(
      expect.objectContaining({
        tipo: "correlacionar",
        conceito_a: "acessos",
        conceito_b: "auditoria",
      }),
    );
    const r = onResultado.mock.calls[0][0];
    expect(r.resposta.papeis).toEqual(["A", "B", "relacao"]);
  });
});
