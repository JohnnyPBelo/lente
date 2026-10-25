import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { reiniciarApiFalsa } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";

describe("REG-BAR-004", () => {
  beforeEach(() => reiniciarApiFalsa());

  it("setas e Enter escolhem Correlacionar; Escape volta a Procurar", async () => {
    const u = userEvent.setup();
    render(<BarraEscrita />);
    await u.click(screen.getByRole("button", { name: copy.bar.menu_hint }));
    expect(screen.getByRole("menu")).toBeInTheDocument();
    await u.keyboard("{ArrowDown}");
    await u.keyboard("{Enter}");
    expect(screen.getByLabelText(copy.bar.correlate_a)).toBeInTheDocument();
    expect(screen.getByLabelText(copy.bar.correlate_b)).toBeInTheDocument();
    await u.keyboard("{Escape}");
    expect(screen.getByLabelText(copy.bar.placeholder_search)).toBeInTheDocument();
    expect(screen.queryByLabelText(copy.bar.correlate_a)).not.toBeInTheDocument();
  });
});
