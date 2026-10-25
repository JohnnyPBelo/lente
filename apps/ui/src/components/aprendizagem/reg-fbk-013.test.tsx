import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { copy } from "../../lib/copy";
import { ExportarCorrecoes } from "./ExportarCorrecoes";

describe("REG-FBK-013", () => {
  it("ecrã de exportação mostra export.warning (trechos saem da máquina)", () => {
    render(<ExportarCorrecoes />);
    expect(screen.getByRole("heading", { name: copy.export.title })).toBeInTheDocument();
    const aviso = screen.getByTestId("export-warning");
    expect(aviso).toHaveTextContent(copy.export.warning);
    expect(aviso.textContent).toBe(copy.export.warning);
  });
});
