import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento, listarFixadosFalsos } from "../../lib/api";

import { MensagemComDocumentos } from "./MensagemComDocumentos";

describe("REG-DOS-002", () => {
  it("citação abre leitor directo; leque disponível", async () => {
    const onCit = vi.fn();
    const onDoc = vi.fn();
    const user = userEvent.setup();
    render(
      <MensagemComDocumentos
        frases={[
          {
            texto: "Frase",
            n: 1,
            destino: { documento_id: "doc_1", pagina: 2, n: 1 },
          },
        ]}
        miniaturas={[
          { documento_id: "doc_1", pagina: 2, url: "/a.webp" },
          { documento_id: "doc_2", pagina: 1, url: "/b.webp" },
        ]}
        onAbrirDoc={onDoc}
        onAbrirCitacao={onCit}
      />,
    );
    await user.click(screen.getByRole("button", { name: /Abrir na página/ }));
    expect(onCit).toHaveBeenCalledWith(
      expect.objectContaining({ documento_id: "doc_1", pagina: 2 }),
    );
    expect(document.querySelectorAll(".miniatura").length).toBeGreaterThan(1);
  });
});
