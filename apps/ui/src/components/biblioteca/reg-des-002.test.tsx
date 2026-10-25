import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import {
  DocumentoLista,
  ListaVirtualizada,
} from "./ListaVirtualizada";

function documentosSinteticos(n: number): DocumentoLista[] {
  return Array.from({ length: n }, (_, i) => ({
    id: `doc_${i}`,
    titulo: `Linha ${i}`,
  }));
}

describe("REG-DES-002", () => {
  it("no scroll o número de nós montados permanece limitado", () => {
    const total = 8000;
    render(
      <ListaVirtualizada
        documentos={documentosSinteticos(total)}
        alturaLinha={36}
        alturaViewport={360}
      />,
    );

    const lista = screen.getByTestId("lista-biblioteca");
    const antes = Number(lista.getAttribute("data-montados"));
    expect(antes).toBeLessThan(100);
    expect(antes).toBeLessThan(total);

    fireEvent.scroll(lista, { target: { scrollTop: 36 * 2000 } });

    const depois = Number(lista.getAttribute("data-montados"));
    const linhas = screen.getAllByTestId("linha-biblioteca");
    expect(depois).toBe(linhas.length);
    expect(depois).toBeLessThan(100);
    expect(depois).toBeLessThan(total);
    // Não monta todas as linhas após scroll.
    expect(screen.queryByText("Linha 0")).not.toBeInTheDocument();
    expect(screen.getByText("Linha 2000")).toBeInTheDocument();
  });
});
