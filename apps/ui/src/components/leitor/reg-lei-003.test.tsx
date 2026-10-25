import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento, listarFixadosFalsos } from "../../lib/api";

import { Leitor } from "./Leitor";

describe("REG-LEI-003", () => {
  beforeEach(() => {
    reiniciarApiFalsa();
    semearDocumento(
      { id: "doc_img", titulo: "Scan", tipo: "imagem", paginas: 1, hash_sha256: "a".repeat(64), desactualizado: false, sumario: [], etiquetas: [] },
      [{ pagina: 1, texto: "", largura: 800, altura: 600 }],
    );
  });

  it("zoom e ajustes; arrastar em imagem", async () => {
    const user = userEvent.setup();
    render(<Leitor documentoId="doc_img" aberto onMinimizar={vi.fn()} />);
    await waitFor(() => expect(screen.getByRole("dialog")).toBeInTheDocument());
    await user.click(screen.getByRole("button", { name: copy.reader.zoom_in }));
    await user.click(screen.getByRole("button", { name: copy.reader.fit_width }));
    expect(document.querySelector('[data-ajuste="largura"]')).toBeTruthy();
    await user.click(screen.getByRole("button", { name: copy.reader.fit_page }));
    expect(document.querySelector('[data-ajuste="pagina"]')).toBeTruthy();
  });
});
