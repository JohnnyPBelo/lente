import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { reiniciarApiFalsa, semearDocumento } from "../../lib/api";
import { Leitor } from "./Leitor";

describe("Leitor.highlights", () => {
  beforeEach(() => {
    reiniciarApiFalsa();
    semearDocumento(
      {
        id: "doc_12",
        titulo: "Politica",
        tipo: "texto",
        paginas: 1,
        hash_sha256: "a".repeat(64),
        desactualizado: false,
        sumario: [],
        etiquetas: [],
      },
      [{ pagina: 1, texto: "ABCDEFGHIJ", largura: 100, altura: 100 }],
      [{ n: 1, pagina: 1, offsets: { inicio: 2, fim: 5 }, mensagem_id: "msg_1" }],
    );
  });
  it("highlight usa offsets literais", async () => {
    render(
      <Leitor
        aberto
        documentoId="doc_12"
        mensagemId="msg_1"
        onMinimizar={() => {}}
      />,
    );
    const mark = await screen.findByText("CDE");
    expect(mark.tagName).toBe("MARK");
    expect(mark).toHaveAttribute("data-inicio", "2");
    expect(mark).toHaveAttribute("data-fim", "5");
    expect(mark).toHaveAttribute("data-literal", "true");
  });
});
