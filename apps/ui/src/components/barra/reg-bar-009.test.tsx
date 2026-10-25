import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { reiniciarApiFalsa, semearAlertasFalsos } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";

describe("REG-BAR-009", () => {
  beforeEach(() => reiniciarApiFalsa());
  it("Alerta: placeholder e criação; limite mostra copy", async () => {
    const u = userEvent.setup();
    const onResultado = vi.fn();
    render(<BarraEscrita onResultado={onResultado} />);
    await u.click(screen.getByRole("button", { name: copy.bar.menu_hint }));
    await u.click(screen.getByRole("menuitem", { name: copy.mode.alert }));
    expect(screen.getByPlaceholderText(copy.bar.alert_placeholder)).toBeInTheDocument();
    await u.type(screen.getByPlaceholderText(copy.bar.alert_placeholder), "VPN{Enter}");
    expect(onResultado).toHaveBeenCalledWith(expect.objectContaining({ tipo: "alerta", ok: true }));

    reiniciarApiFalsa();
    semearAlertasFalsos(10);
    onResultado.mockClear();
    render(<BarraEscrita onResultado={onResultado} />);
    await u.click(screen.getAllByRole("button", { name: copy.bar.menu_hint })[1]!);
    await u.click(screen.getAllByRole("menuitem", { name: copy.mode.alert })[0]!);
    await u.type(screen.getAllByPlaceholderText(copy.bar.alert_placeholder)[0]!, "outro{Enter}");
    expect(await screen.findByRole("alert")).toHaveTextContent(copy.alerts.limit);
  });
});
