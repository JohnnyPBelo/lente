import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { reiniciarApiFalsa, semearDocumento } from "../../lib/api";
import { copy } from "../../lib/copy";
import { Leitor } from "./Leitor";

describe("clip debug", () => {
  it("writes with prototype redefine", async () => {
    reiniciarApiFalsa();
    const writeText = vi.fn().mockResolvedValue(undefined);
    const clip = { writeText };
    Object.defineProperty(window.Navigator.prototype, "clipboard", {
      configurable: true,
      get() {
        return clip;
      },
    });
    console.log("same?", navigator.clipboard.writeText === writeText);

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
    vi.spyOn(window, "getSelection").mockReturnValue({
      toString: () => "texto seleccionado aqui",
      removeAllRanges: () => {},
      addRange: () => {},
    } as unknown as Selection);
    const user = userEvent.setup();
    render(<Leitor documentoId="doc_c" aberto onMinimizar={vi.fn()} />);
    await screen.findByText(/texto seleccionado/);
    document
      .querySelector(".leitor-superficie")!
      .dispatchEvent(new MouseEvent("mouseup", { bubbles: true }));
    const btn = await screen.findByRole("button", { name: copy.reader.copy });
    await user.click(btn);
    await waitFor(() => expect(writeText).toHaveBeenCalled());
    writeText.mockClear();
    await user.click(
      screen.getByRole("button", { name: copy.reader.copy_citation }),
    );
    await waitFor(() => expect(writeText).toHaveBeenCalled());
    const args = writeText.mock.calls.map((c) => String(c[0]));
    expect(args.some((a) => a.includes("Politica.pdf") && a.includes("p. 1"))).toBe(true);
  });
});
