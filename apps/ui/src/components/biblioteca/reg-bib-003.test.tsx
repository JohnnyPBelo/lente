import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import {
  DocumentoLista,
  ListaVirtualizada,
} from "./ListaVirtualizada";

function documentosSinteticos(n: number): DocumentoLista[] {
  return Array.from({ length: n }, (_, i) => ({
    id: `doc_${i}`,
    titulo: `Documento sintético ${i}`,
  }));
}

describe("REG-BIB-003", () => {
  it("com milhares de documentos só monta uma janela, não o total", () => {
    const total = 5000;
    render(
      <ListaVirtualizada
        documentos={documentosSinteticos(total)}
        alturaLinha={36}
        alturaViewport={360}
      />,
    );

    const lista = screen.getByTestId("lista-biblioteca");
    const montados = Number(lista.getAttribute("data-montados"));
    const declarado = Number(lista.getAttribute("data-total"));
    const linhas = screen.getAllByTestId("linha-biblioteca");

    expect(declarado).toBe(total);
    expect(montados).toBe(linhas.length);
    expect(montados).toBeGreaterThan(0);
    expect(montados).toBeLessThan(total);
    // Janela ≈ viewport/linha + sobrejanela; bem abaixo de milhares.
    expect(montados).toBeLessThan(100);
  });
});
