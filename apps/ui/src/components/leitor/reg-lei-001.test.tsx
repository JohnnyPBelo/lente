import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento, listarFixadosFalsos } from "../../lib/api";

import { Leitor } from "./Leitor";

const tipos = ["pdf", "texto", "markdown", "url", "imagem"] as const;

describe("REG-LEI-001", () => {
  beforeEach(() => reiniciarApiFalsa());

  it.each(tipos)("documento %s navegável no leitor", async (tipo) => {
    semearDocumento(
      { id: `doc_${tipo}`, titulo: tipo, tipo, paginas: 3, hash_sha256: "a".repeat(64), desactualizado: false, sumario: [], etiquetas: [] },
      [
        { pagina: 1, texto: "p1 completo", largura: 595, altura: 842 },
        { pagina: 2, texto: "p2 completo", largura: 595, altura: 842 },
        { pagina: 3, texto: "p3 completo", largura: 595, altura: 842 },
      ],
    );
    render(<Leitor documentoId={`doc_${tipo}`} aberto onMinimizar={vi.fn()} />);
    await waitFor(() => expect(screen.getByRole("dialog")).toHaveAttribute("data-tipo", tipo));
    expect(screen.getByLabelText(copy.reader.goto_page)).toBeInTheDocument();
  });
});
