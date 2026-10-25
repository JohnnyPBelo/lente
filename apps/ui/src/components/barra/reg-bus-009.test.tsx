import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { definirLimiarFalso, reiniciarApiFalsa } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BarraEscrita } from "./BarraEscrita";

describe("REG-BUS-009", () => {
  beforeEach(() => {
    reiniciarApiFalsa();
    definirLimiarFalso(0.62);
  });
  it("limiar numérico visível na interface", async () => {
    render(<BarraEscrita />);
    expect(await screen.findByTestId("limiar-visivel")).toHaveTextContent(
      `${copy.chat.threshold}: 0.62`,
    );
  });
});
