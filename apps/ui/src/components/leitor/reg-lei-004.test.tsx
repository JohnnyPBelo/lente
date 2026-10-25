import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento } from "../../lib/api";
import { Leitor } from "./Leitor";

describe("REG-LEI-004", () => {
  beforeEach(() => {
    reiniciarApiFalsa();
    semearDocumento(
      {
        id: "doc_p",
        titulo: "Pag",
        tipo: "texto",
        paginas: 3,
        hash_sha256: "a".repeat(64),
        desactualizado: false,
        sumario: [],
        etiquetas: [],
      },
      [
        { pagina: 1, texto: "alfa", largura: 595, altura: 842 },
        { pagina: 2, texto: "palavra secreta aqui", largura: 595, altura: 842 },
        { pagina: 3, texto: "gama", largura: 595, altura: 842 },
      ],
    );
  });

  it("ir à página e procurar neste documento", async () => {
    const user = userEvent.setup();
    render(<Leitor documentoId="doc_p" aberto onMinimizar={vi.fn()} />);
    await waitFor(() => expect(screen.getByRole("dialog")).toBeInTheDocument());
    const pag = screen.getByLabelText(copy.reader.goto_page);
    fireEvent.change(pag, { target: { value: "2" } });
    fireEvent.blur(pag);
    await waitFor(() => expect(pag).toHaveValue(2));
    const procura = screen.getByLabelText(copy.reader.find_in_doc);
    await user.type(procura, "secreta{Enter}");
    expect(screen.getByRole("status")).toHaveTextContent("secreta");
  });
});
