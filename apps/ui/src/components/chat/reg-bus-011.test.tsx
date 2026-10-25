import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento, listarFixadosFalsos } from "../../lib/api";

import { MensagemComDocumentos } from "./MensagemComDocumentos";

describe("REG-BUS-011", () => {
  it("três cores A/B/relação e miniaturas no leque", () => {
    const onAbrir = vi.fn();
    render(
      <MensagemComDocumentos
        correlacionar
        excertos={[
          { n: 1, papel: "A", documento_id: "doc_1", pagina: 1, texto: "Acesso" },
          { n: 2, papel: "B", documento_id: "doc_2", pagina: 1, texto: "Auditoria" },
          { n: 3, papel: "relacao", documento_id: "doc_1", pagina: 2, texto: "Ligação" },
        ]}
        miniaturas={[
          { documento_id: "doc_1", pagina: 1, url: "/t1.webp" },
          { documento_id: "doc_2", pagina: 1, url: "/t2.webp" },
        ]}
        onAbrirDoc={onAbrir}
        onAbrirCitacao={vi.fn()}
      />,
    );
    expect(screen.getByText(copy.correlate.legend_a)).toBeInTheDocument();
    expect(screen.getByText(copy.correlate.legend_b)).toBeInTheDocument();
    expect(screen.getByText(copy.correlate.legend_relation)).toBeInTheDocument();
    expect(document.querySelectorAll("[data-papel]")).toHaveLength(3);
    expect(document.querySelectorAll(".miniatura")).toHaveLength(2);
  });
});
