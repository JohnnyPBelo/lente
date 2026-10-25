import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { reiniciarApiFalsa } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";

describe("REG-BAR-006", () => {
  beforeEach(() => reiniciarApiFalsa());
  it("Procurar: uma linha e Enter envia", async () => {
    const u = userEvent.setup();
    const onResultado = vi.fn();
    render(<BarraEscrita onResultado={onResultado} />);
    const campo = screen.getByLabelText(copy.bar.placeholder_search);
    expect(campo.tagName).toBe("INPUT");
    await u.type(campo, "acesso remoto{Enter}");
    expect(onResultado).toHaveBeenCalledWith(
      expect.objectContaining({ tipo: "procurar", texto: "acesso remoto" }),
    );
  });
});
