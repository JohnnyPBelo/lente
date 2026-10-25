import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento, listarFixadosFalsos } from "../../lib/api";

import { Highlights } from "./Highlights";

describe("REG-JUI-003", () => {
  it("highlight usa offsets literais da ingestão", () => {
    const texto = "ABCDEFGHIJ";
    render(
      <Highlights
        textoPagina={texto}
        pagina={1}
        marcas={[{ n: 1, pagina: 1, offsets: { inicio: 2, fim: 5 }, caixas: [{ pagina: 1, x: 0, y: 0, w: 10, h: 10 }] }]}
      />,
    );
    const mark = document.querySelector("mark.highlight")!;
    expect(mark).toHaveAttribute("data-literal", "true");
    expect(mark).toHaveAttribute("data-inicio", "2");
    expect(mark).toHaveAttribute("data-fim", "5");
    expect(mark.textContent).toBe("CDE");
  });
});
