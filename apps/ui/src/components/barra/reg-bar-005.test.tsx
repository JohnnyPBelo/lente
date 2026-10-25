import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { reiniciarApiFalsa } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";

describe("REG-BAR-005", () => {
  beforeEach(() => reiniciarApiFalsa());
  it("pastilha mostra o modo activo", async () => {
    const u = userEvent.setup();
    render(<BarraEscrita />);
    await u.click(screen.getByRole("button", { name: copy.bar.menu_hint }));
    await u.click(screen.getByRole("menuitem", { name: copy.mode.alert }));
    expect(screen.getByRole("status")).toHaveTextContent(copy.mode.alert);
  });
});
