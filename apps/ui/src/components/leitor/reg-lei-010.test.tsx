import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento, listarFixadosFalsos } from "../../lib/api";

import { Leitor } from "./Leitor";

describe("REG-LEI-010", () => {
  beforeEach(() => {
    reiniciarApiFalsa();
    semearDocumento(
      { id: "doc_cf", titulo: "C", tipo: "texto", paginas: 1, hash_sha256: "a".repeat(64), desactualizado: false, sumario: [], etiquetas: [] },
      [{ pagina: 1, texto: "trecho confrontar", largura: 595, altura: 842 }],
    );
  });

  it("bolha Confrontar preenche selecção", async () => {
    const onConf = vi.fn();
    const user = userEvent.setup();
    render(
      <Leitor documentoId="doc_cf" aberto onConfrontarSelecao={onConf} onMinimizar={vi.fn()} />,
    );
    await waitFor(() => expect(screen.getByRole("dialog")).toBeInTheDocument());
    vi.spyOn(window, "getSelection").mockReturnValue({
      toString: () => "trecho confrontar",
      removeAllRanges: () => undefined,
      addRange: () => undefined,
    } as unknown as Selection);
    document.querySelector(".leitor-superficie")!.dispatchEvent(
      new MouseEvent("mouseup", { bubbles: true }),
    );
    await waitFor(() => expect(screen.getByRole("button", { name: copy.reader.bubble_confront })).toBeInTheDocument());
    await user.click(screen.getByRole("button", { name: copy.reader.bubble_confront }));
    expect(onConf).toHaveBeenCalledWith(
      "trecho confrontar",
      expect.objectContaining({ documento_id: "doc_cf", pagina: 1 }),
    );
  });
});
