import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { reiniciarApiFalsa } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";

describe("REG-BAR-002", () => {
  beforeEach(() => reiniciarApiFalsa());
  it("botão + abre menu vidro com modos", async () => {
    const u = userEvent.setup();
    render(<BarraEscrita />);
    await u.click(screen.getByRole("button", { name: copy.bar.menu_hint }));
    const menu = screen.getByRole("menu");
    expect(menu).toHaveClass("vidro");
    expect(screen.getByRole("menuitem", { name: copy.mode.search })).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: copy.mode.correlate })).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: copy.mode.confront })).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: copy.mode.alert })).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: copy.mode.gaps })).toBeInTheDocument();
    expect(screen.queryByRole("menuitem", { name: copy.learn.export })).not.toBeInTheDocument();
  });
});
