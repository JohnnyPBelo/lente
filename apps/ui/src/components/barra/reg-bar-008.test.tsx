import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { reiniciarApiFalsa } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";

describe("REG-BAR-008", () => {
  beforeEach(() => reiniciarApiFalsa());
  it("Confrontar: Trecho A/B, Escolher, texto colado e leitura", async () => {
    const u = userEvent.setup();
    const onResultado = vi.fn();
    render(<BarraEscrita onResultado={onResultado} />);
    await u.click(screen.getByRole("button", { name: copy.bar.menu_hint }));
    await u.click(screen.getByRole("menuitem", { name: copy.mode.confront }));
    expect(screen.getByLabelText(copy.bar.confront_a)).toBeInTheDocument();
    expect(screen.getByLabelText(copy.bar.confront_b)).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: copy.bar.confront_choose })).toHaveLength(2);
    await u.type(screen.getByLabelText(copy.bar.confront_a), "O prazo é 90 dias.");
    await u.type(screen.getByLabelText(copy.bar.confront_b), "O refeitório fecha às 15:00.");
    await u.click(screen.getByRole("button", { name: copy.bar.send }));
    expect(onResultado).toHaveBeenCalled();
    const r = onResultado.mock.calls[0][0];
    expect(["concordam", "contradizem-se", "assuntos_diferentes"]).toContain(r.resposta.leitura);
    expect(r.resposta).toHaveProperty("score");
  });
});
