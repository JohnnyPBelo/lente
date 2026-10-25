import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento, listarFixadosFalsos } from "../../lib/api";

import { Leitor } from "./Leitor";

describe("REG-LEI-009", () => {
  beforeEach(() => {
    reiniciarApiFalsa();
    semearDocumento(
      { id: "doc_r", titulo: "R", tipo: "texto", paginas: 1, hash_sha256: "a".repeat(64), desactualizado: false, sumario: [], etiquetas: [] },
      [{ pagina: 1, texto: "serif", largura: 595, altura: 842 }],
    );
  });

  it("superfície sólida serif vs chrome vidro", async () => {
    render(<Leitor documentoId="doc_r" aberto onMinimizar={vi.fn()} />);
    await waitFor(() => expect(screen.getByRole("dialog")).toBeInTheDocument());
    expect(document.querySelector(".leitor-superficie")).toHaveAttribute("data-superficie", "solida");
    expect(screen.getByRole("dialog")).toHaveAttribute("data-serif", "true");
    expect(document.querySelector(".leitor-ferramentas.vidro")).toBeTruthy();
  });
});
