import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { reiniciarApiFalsa } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";
import { prefixoEmbedding } from "../../lib/lentes";

describe("REG-BAR-011", () => {
  beforeEach(() => reiniciarApiFalsa());
  it("lente ao lado do modo; Confrontar não muda leituras", async () => {
    const u = userEvent.setup();
    const onResultado = vi.fn();
    render(<BarraEscrita onResultado={onResultado} />);
    const select = screen.getByLabelText("Lente de trabalho");
    await u.selectOptions(select, "verificar");
    expect(select).toHaveValue("verificar");
    await u.click(screen.getByRole("button", { name: copy.bar.menu_hint }));
    await u.click(screen.getByRole("menuitem", { name: copy.mode.alert }));
    expect(screen.getByRole("status")).toHaveTextContent(copy.mode.alert);
    expect(prefixoEmbedding("verificar", "alerta", "x")).toContain("fact checking");
    expect(prefixoEmbedding("investigar", "confrontar", "x")).toContain("search result");
  });
});
