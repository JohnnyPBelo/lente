import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { reiniciarApiFalsa } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";

describe("REG-BAR-003", () => {
  beforeEach(() => reiniciarApiFalsa());
  it("/ abre o mesmo menu que +", async () => {
    const u = userEvent.setup();
    render(<BarraEscrita />);
    const campo = screen.getByLabelText(copy.bar.placeholder_search);
    await u.click(campo);
    await u.keyboard("/");
    expect(screen.getByRole("menu")).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: copy.mode.correlate })).toBeInTheDocument();
  });
});
