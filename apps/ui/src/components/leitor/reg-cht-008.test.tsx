import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento, listarFixadosFalsos } from "../../lib/api";

import { MensagemComDocumentos } from "../chat/MensagemComDocumentos";
import { Leitor } from "./Leitor";

describe("REG-CHT-008", () => {
  beforeEach(() => {
    reiniciarApiFalsa();
    semearDocumento(
      { id: "doc_1", titulo: "Doc", tipo: "texto", paginas: 1, hash_sha256: "a".repeat(64), desactualizado: false, sumario: [], etiquetas: [] },
      [{ pagina: 1, texto: "O acesso remoto exige aprovação.", largura: 595, altura: 842 }],
      [{ n: 1, pagina: 1, offsets: { inicio: 0, fim: 10 } }],
    );
  });

  it("fluxo com animações e serif no leitor / Geist no chrome", async () => {
    const onMin = vi.fn();
    const user = userEvent.setup();
    const { rerender } = render(
      <>
        <MensagemComDocumentos
          miniaturas={[{ documento_id: "doc_1", pagina: 1, url: "/t.webp" }]}
          onAbrirDoc={vi.fn()}
          onAbrirCitacao={vi.fn()}
        />
        <Leitor documentoId="doc_1" aberto highlightN={1} onMinimizar={onMin} />
      </>,
    );
    expect(document.querySelector(".mensagem-docs")).toHaveAttribute("data-animacao", "entrada");
    await waitFor(() => expect(screen.getByRole("dialog")).toHaveAttribute("data-serif", "true"));
    expect(document.querySelector(".leitor-ferramentas.vidro")).toBeTruthy();
    await user.click(screen.getByRole("button", { name: copy.reader.minimize }));
    expect(onMin).toHaveBeenCalled();
    rerender(
      <>
        <MensagemComDocumentos
          miniaturas={[{ documento_id: "doc_1", pagina: 1, url: "/t.webp" }]}
          onAbrirDoc={vi.fn()}
          onAbrirCitacao={vi.fn()}
        />
        <Leitor documentoId="doc_1" aberto={false} onMinimizar={onMin} />
      </>,
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
