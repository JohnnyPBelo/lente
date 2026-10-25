import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento, listarFixadosFalsos } from "../../lib/api";

import { Leitor } from "./Leitor";

describe("REG-LEI-005", () => {
  beforeEach(() => {
    reiniciarApiFalsa();
    semearDocumento(
      {
        id: "doc_s",
        titulo: "Sum",
        tipo: "texto",
        paginas: 2,
        hash_sha256: "a".repeat(64),
        desactualizado: false,
        sumario: [{ titulo: "Secção B", pagina: 2 }],
        etiquetas: [],
      },
      [
        { pagina: 1, texto: "a", largura: 595, altura: 842 },
        { pagina: 2, texto: "b", largura: 595, altura: 842 },
      ],
    );
  });

  it("sumário navega para a secção", async () => {
    const user = userEvent.setup();
    render(<Leitor documentoId="doc_s" aberto onMinimizar={vi.fn()} />);
    await waitFor(() => expect(screen.getByRole("dialog")).toBeInTheDocument());
    await user.click(screen.getByRole("button", { name: copy.reader.toc }));
    await user.click(screen.getByRole("button", { name: "Secção B" }));
    expect(screen.getByLabelText(copy.reader.goto_page)).toHaveValue(2);
  });
});
