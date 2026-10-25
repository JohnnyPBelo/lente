import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento, listarFixadosFalsos } from "../../lib/api";

import { Leitor } from "./Leitor";

describe("REG-LEI-011", () => {
  beforeEach(() => {
    reiniciarApiFalsa();
    semearDocumento(
      { id: "doc_h", titulo: "H", tipo: "texto", paginas: 1, hash_sha256: "a".repeat(64), desactualizado: false, sumario: [], etiquetas: [] },
      [{ pagina: 1, texto: "ABCDEFGHIJ", largura: 595, altura: 842 }],
      [{ n: 3, pagina: 1, offsets: { inicio: 2, fim: 6 } }],
    );
  });

  it("highlight acende uma vez; minimizar regressa", async () => {
    const onMin = vi.fn();
    const user = userEvent.setup();
    render(
      <Leitor documentoId="doc_h" aberto highlightN={3} onMinimizar={onMin} />,
    );
    await waitFor(() => expect(document.querySelector(".highlight--aceso")).toBeTruthy());
    await user.click(screen.getByRole("button", { name: copy.reader.minimize }));
    expect(onMin).toHaveBeenCalled();
  });
});
