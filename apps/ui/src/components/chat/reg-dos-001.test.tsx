import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento, listarFixadosFalsos } from "../../lib/api";

import { MensagemComDocumentos } from "./MensagemComDocumentos";

describe("REG-DOS-001", () => {
  it("frases são links activáveis", () => {
    render(
      <MensagemComDocumentos
        frases={[
          {
            texto: "O acesso remoto exige aprovação.",
            n: 1,
            destino: { documento_id: "doc_1", pagina: 1, n: 1 },
          },
        ]}
        miniaturas={[]}
        onAbrirDoc={vi.fn()}
        onAbrirCitacao={vi.fn()}
      />,
    );
    expect(screen.getByRole("button", { name: /Abrir na página/ })).toBeInTheDocument();
  });
});
