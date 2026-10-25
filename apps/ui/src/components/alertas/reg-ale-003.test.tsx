import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { copy } from "../../lib/copy";
import { GrupoAlertas } from "./GrupoAlertas";

describe("REG-ALE-003", () => {
  it("mostra o grupo Alertas por baixo das conversas", () => {
    render(
      <nav aria-label={copy.a11y.sidebar}>
        <section aria-label={copy.conversations.group}>
          <h2>{copy.conversations.group}</h2>
          <ul role="list" aria-label={copy.conversations.group}>
            <li>Procura de exemplo</li>
          </ul>
        </section>
        <GrupoAlertas
          alertas={[
            {
              id: "ale_1",
              texto: "Novas menções a VPN",
              activo: true,
              chat_id: "cht_al_1",
            },
          ]}
        />
      </nav>,
    );

    const lateral = screen.getByRole("navigation", { name: copy.a11y.sidebar });
    const conversas = within(lateral).getByRole("heading", {
      name: copy.conversations.group,
    });
    const alertas = within(lateral).getByRole("heading", {
      name: copy.alerts.group,
    });

    expect(copy.alerts.group).toBe("Alertas");
    expect(alertas).toBeInTheDocument();
    // Grupo Alertas depois das conversas no DOM.
    expect(
      conversas.compareDocumentPosition(alertas) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    expect(within(lateral).getByText("Novas menções a VPN")).toBeInTheDocument();
  });
});
