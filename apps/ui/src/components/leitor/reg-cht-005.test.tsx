import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento, listarFixadosFalsos } from "../../lib/api";

import { Leitor } from "./Leitor";

describe("REG-CHT-005", () => {
  beforeEach(() => {
    reiniciarApiFalsa();
    semearDocumento(
      { id: "doc_1", titulo: "Política", tipo: "texto", paginas: 2, hash_sha256: "a".repeat(64), desactualizado: false, sumario: [], etiquetas: [] },
      [{ pagina: 1, texto: "texto", largura: 595, altura: 842 }],
    );
  });

  it("minimizar e Escape recolhem o leitor", async () => {
    const onMin = vi.fn();
    const user = userEvent.setup();
    render(
      <Leitor documentoId="doc_1" aberto onMinimizar={onMin} />,
    );
    await waitFor(() => expect(screen.getByRole("dialog")).toBeInTheDocument());
    await user.click(screen.getByRole("button", { name: copy.reader.minimize }));
    expect(onMin).toHaveBeenCalled();
    onMin.mockClear();
    await user.keyboard("{Escape}");
    expect(onMin).toHaveBeenCalled();
  });
});
