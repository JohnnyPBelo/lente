import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { reiniciarApiFalsa } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";

describe("REG-BAR-001", () => {
  beforeEach(() => reiniciarApiFalsa());
  it("interacção fica na barra sem navegar", () => {
    render(<BarraEscrita />);
    const barra = screen.getByLabelText(copy.a11y.write_bar);
    expect(barra).toHaveAttribute("data-slot", "barra-escrita");
    expect(window.location.pathname).toBe("/");
  });
});
