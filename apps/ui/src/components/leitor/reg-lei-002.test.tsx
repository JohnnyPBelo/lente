import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento } from "../../lib/api";
import { Leitor } from "./Leitor";

describe("REG-LEI-002", () => {
  beforeEach(() => {
    reiniciarApiFalsa();
    semearDocumento(
      {
        id: "doc_m",
        titulo: "Multi",
        tipo: "texto",
        paginas: 3,
        hash_sha256: "a".repeat(64),
        desactualizado: false,
        sumario: [],
        etiquetas: [],
      },
      [
        { pagina: 1, texto: "aaaBBBBccc", largura: 595, altura: 842 },
        { pagina: 2, texto: "ddddEEEEff", largura: 595, altura: 842 },
        { pagina: 3, texto: "gggg", largura: 595, altura: 842 },
      ],
      [
        { n: 1, pagina: 1, offsets: { inicio: 3, fim: 7 } },
        { n: 2, pagina: 2, offsets: { inicio: 4, fim: 8 } },
      ],
    );
  });

  it("scroll contínuo e salto entre marcas", async () => {
    const user = userEvent.setup();
    render(
      <Leitor
        documentoId="doc_m"
        aberto
        highlightN={1}
        onMinimizar={vi.fn()}
      />,
    );
    await waitFor(() => expect(screen.getByRole("dialog")).toBeInTheDocument());
    expect(document.querySelector('[data-scroll="continuo"]')).toBeTruthy();
    await user.click(screen.getByRole("button", { name: copy.reader.next_mark }));
    await waitFor(() =>
      expect(screen.getByLabelText(copy.reader.goto_page)).toHaveValue(2),
    );
  });
});
