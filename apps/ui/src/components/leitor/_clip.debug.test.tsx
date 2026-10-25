import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { reiniciarApiFalsa, semearDocumento } from "../../lib/api";
import { copy } from "../../lib/copy";
import { Leitor } from "./Leitor";

describe("clip debug", () => {
  it("writes", async () => {
    reiniciarApiFalsa();
    const writeText = vi.fn().mockResolvedValue(undefined);
    // @ts-expect-error test
    navigator.clipboard = { writeText };
    console.log(
      "same ref?",
      navigator.clipboard.writeText === writeText,
      Object.getOwnPropertyDescriptor(navigator, "clipboard"),
    );
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
    console.log("after click", writeText.mock.calls);
    await navigator.clipboard.writeText("direct");
    console.log("after direct", writeText.mock.calls);
    expect(writeText.mock.calls.length).toBeGreaterThan(0);
  });
});
