import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { MensagemComDocumentos } from "./MensagemComDocumentos";

describe("lacunas ausente sem Abrir na página (issue #75)", () => {
  it("só linhas com documento_id têm citação clicável", () => {
    render(
      <MensagemComDocumentos
        miniaturas={[]}
        onAbrirDoc={vi.fn()}
        onAbrirCitacao={vi.fn()}
        frases={[
          {
            texto: "encontrado: biodiversidade no rio Douro",
            n: 1,
            destino: { n: 1, documento_id: "doc_1", pagina: 1 },
          },
          {
            texto: "ausente: energia nuclear em Marte",
            n: 2,
            destino: null,
          },
        ]}
      />,
    );
    const botoes = screen.getAllByRole("button", {
      name: new RegExp(copy.chat.open_source),
    });
    expect(botoes).toHaveLength(1);
    expect(botoes[0]).toHaveAttribute("data-documento-id", "doc_1");
    expect(
      screen.getByText(/ausente: energia nuclear em Marte/),
    ).toBeInTheDocument();
  });
});
