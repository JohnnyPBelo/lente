import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { reiniciarApiFalsa } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";

describe("REG-A11-002", () => {
  beforeEach(() => reiniciarApiFalsa());
  it("só teclado: menu, modo, Escape a Procurar", async () => {
    const u = userEvent.setup();
    render(<BarraEscrita />);
    const mais = screen.getByRole("button", { name: copy.bar.menu_hint });
    expect(mais).toHaveAccessibleName(copy.bar.menu_hint);
    await u.tab();
    // focar + e activar
    mais.focus();
    await u.keyboard("{Enter}");
    expect(screen.getByRole("menu")).toBeInTheDocument();
    await u.keyboard("{ArrowDown}{ArrowDown}{ArrowDown}{Enter}");
    expect(screen.getByRole("status")).toBeInTheDocument();
    await u.keyboard("{Escape}");
    expect(screen.getByLabelText(copy.bar.placeholder_search)).toBeInTheDocument();
  });
});
