import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it } from "vitest";
import { copy } from "../../lib/copy";
import { FioAlerta } from "./FioAlerta";

function FioComEstado() {
  const [activo, setActivo] = useState(true);
  return (
    <FioAlerta
      alertaId="ale_1"
      titulo="Novas menções a VPN"
      activo={activo}
      onAlternar={setActivo}
    />
  );
}

describe("REG-ALE-007", () => {
  it("o interruptor no topo desliga o alerta até voltar a ligar", async () => {
    const utilizador = userEvent.setup();
    render(<FioComEstado />);

    const interruptor = screen.getByRole("switch", {
      name: copy.alerts.toggle_on,
    });
    expect(interruptor).toHaveAttribute("aria-checked", "true");

    await utilizador.click(interruptor);

    const desligado = screen.getByRole("switch", {
      name: copy.alerts.toggle_off,
    });
    expect(desligado).toHaveAttribute("aria-checked", "false");

    await utilizador.click(desligado);
    expect(
      screen.getByRole("switch", { name: copy.alerts.toggle_on }),
    ).toHaveAttribute("aria-checked", "true");
  });
});
