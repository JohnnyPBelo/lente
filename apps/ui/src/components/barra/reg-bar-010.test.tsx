import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { reiniciarApiFalsa } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";

describe("REG-BAR-010", () => {
  beforeEach(() => reiniciarApiFalsa());
  it("Lacunas: multilinha, Enter envia, sem escritor", async () => {
    const u = userEvent.setup();
    const onResultado = vi.fn();
    render(<BarraEscrita onResultado={onResultado} />);
    await u.click(screen.getByRole("button", { name: copy.bar.menu_hint }));
    await u.click(screen.getByRole("menuitem", { name: copy.mode.gaps }));
    const caixa = screen.getByLabelText(copy.bar.gaps_placeholder);
    expect(caixa.tagName).toBe("TEXTAREA");
    await u.type(caixa, "Política de palavras-passe?{Shift>}{Enter}{/Shift}Formação anual?");
    await u.keyboard("{Enter}");
    expect(onResultado).toHaveBeenCalled();
    const r = onResultado.mock.calls[0][0];
    expect(r.tipo).toBe("lacunas");
    expect(r.resposta.escritor_chamado).toBe(false);
    expect(r.resposta.itens.length).toBeGreaterThanOrEqual(1);
    for (const item of r.resposta.itens) {
      expect(["encontrado", "fraco", "ausente"]).toContain(item.estado);
    }
  });
});
