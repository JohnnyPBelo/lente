import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento } from "../../lib/api";
import { Leitor } from "./Leitor";

describe("REG-LEI-006", () => {
  const writeText = vi.fn().mockResolvedValue(undefined);

  beforeEach(() => {
    reiniciarApiFalsa();
    writeText.mockClear();
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText },
    });
    semearDocumento(
      {
        id: "doc_c",
        titulo: "Politica.pdf",
        tipo: "texto",
        paginas: 1,
        hash_sha256: "a".repeat(64),
        desactualizado: false,
        sumario: [],
        etiquetas: [],
      },
      [{ pagina: 1, texto: "texto seleccionado aqui", largura: 595, altura: 842 }],
    );
  });

  it("copiar texto e citação com ficheiro e página", async () => {
    vi.spyOn(window, "getSelection").mockReturnValue({
      toString: () => "texto seleccionado aqui",
      removeAllRanges: () => {},
      addRange: () => {},
    } as unknown as Selection);

    render(<Leitor documentoId="doc_c" aberto onMinimizar={vi.fn()} />);
    await waitFor(() => expect(screen.getByRole("dialog")).toBeInTheDocument());
    await screen.findByText(/texto seleccionado/);

    fireEvent.mouseUp(document.querySelector(".leitor-superficie")!);

    const copiar = await screen.findByRole("button", { name: copy.reader.copy });
    fireEvent.click(copiar);
    expect(writeText).toHaveBeenCalledWith("texto seleccionado aqui");

    fireEvent.click(
      screen.getByRole("button", { name: copy.reader.copy_citation }),
    );
    const args = writeText.mock.calls.map((c) => String(c[0]));
    expect(
      args.some((a) => a.includes("Politica.pdf") && a.includes("p. 1")),
    ).toBe(true);
  });
});
