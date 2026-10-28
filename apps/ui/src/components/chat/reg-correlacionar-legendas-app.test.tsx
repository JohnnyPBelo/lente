import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { MensagemComDocumentos } from "./MensagemComDocumentos";

describe("correlacionar legendas no fio (issue #74)", () => {
  it("passa correlacionar=true e mostra A/B/Relação sem frases planas", () => {
    render(
      <MensagemComDocumentos
        correlacionar
        excertos={[
          {
            n: 1,
            papel: "A",
            documento_id: "doc_1",
            pagina: 1,
            texto: "biodiversidade aquática",
          },
          {
            n: 2,
            papel: "B",
            documento_id: "doc_2",
            pagina: 1,
            texto: "mitigação de impacto",
          },
          {
            n: 3,
            papel: "relacao",
            documento_id: "doc_1",
            pagina: 2,
            texto: "relação entre habitats e mitigação",
          },
        ]}
        miniaturas={[
          { documento_id: "doc_1", pagina: 1, url: "/t1.webp" },
          { documento_id: "doc_2", pagina: 1, url: "/t2.webp" },
        ]}
        frases={[]}
        onAbrirDoc={vi.fn()}
        onAbrirCitacao={vi.fn()}
      />,
    );
    expect(screen.getByText(copy.correlate.legend_a)).toBeInTheDocument();
    expect(screen.getByText(copy.correlate.legend_b)).toBeInTheDocument();
    expect(screen.getByText(copy.correlate.legend_relation)).toBeInTheDocument();
    expect(document.querySelectorAll("[data-papel]")).toHaveLength(3);
    expect(
      screen.queryByRole("button", { name: new RegExp(copy.chat.open_source) }),
    ).not.toBeInTheDocument();
  });
});
