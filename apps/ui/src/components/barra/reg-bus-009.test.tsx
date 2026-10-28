import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { definirLimiarFalso, reiniciarApiFalsa } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";

describe("REG-BUS-009", () => {
  beforeEach(() => {
    reiniciarApiFalsa();
  });
  it("limiar numérico visível na interface (Platt)", async () => {
    definirLimiarFalso(0.62, { platt_activo: true });
    render(<BarraEscrita />);
    expect(await screen.findByTestId("limiar-visivel")).toHaveTextContent(
      `${copy.chat.threshold}: 0.62`,
    );
  });
  it("limiar bruto 0 comunica ausência de calibração (issue #77)", async () => {
    definirLimiarFalso(0, { platt_activo: false });
    render(<BarraEscrita />);
    const el = await screen.findByTestId("limiar-visivel");
    expect(el).toHaveTextContent(`${copy.chat.threshold_raw}: 0`);
    expect(el).toHaveTextContent(copy.chat.threshold_uncalibrated);
    expect(el).toHaveAttribute("data-platt", "false");
  });
});
