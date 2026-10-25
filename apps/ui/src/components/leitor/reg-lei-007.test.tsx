import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento, listarFixadosFalsos } from "../../lib/api";

import { Leitor } from "./Leitor";

describe("REG-LEI-007", () => {
  beforeEach(() => {
    reiniciarApiFalsa();
    semearDocumento(
      { id: "doc_f", titulo: "F", tipo: "texto", paginas: 1, hash_sha256: "a".repeat(64), desactualizado: false, sumario: [], etiquetas: [] },
      [{ pagina: 1, texto: "NEGATIVOpositivoEXTRA", largura: 595, altura: 842 }],
      [{ n: 1, pagina: 1, offsets: { inicio: 0, fim: 8 } }],
    );
  });

  it("Corrigir usa selecção positiva e marcas negativas", async () => {
    const onCorr = vi.fn();
    render(
      <Leitor
        documentoId="doc_f"
        aberto
        corrigirActivo
        onCorrigirSelecao={onCorr}
        onMinimizar={vi.fn()}
      />,
    );
    await waitFor(() => expect(screen.getByRole("dialog")).toBeInTheDocument());
    const texto = document.querySelector(".leitor-texto")!;
    // select "positivo" chars 8-16
    const range = document.createRange();
    // fallback: whole text and assert called with slice logic by dispatching with mocked selection
    const selMock = {
      toString: () => "positivo",
      removeAllRanges: () => undefined,
      addRange: () => undefined,
    };
    vi.spyOn(window, "getSelection").mockReturnValue(selMock as unknown as Selection);
    texto.dispatchEvent(new MouseEvent("mouseup", { bubbles: true }));
    expect(onCorr).toHaveBeenCalledWith("positivo", ["NEGATIVO"]);
  });
});
