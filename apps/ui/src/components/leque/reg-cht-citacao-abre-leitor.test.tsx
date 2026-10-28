import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LequeLeitor } from "./LequeLeitor";

describe("citação abre o leitor (issue #73)", () => {
  it("destinoInicial abre o dialog do leitor sem clicar na miniatura", () => {
    render(
      <LequeLeitor
        mensagemId="msg_1"
        chatId="cht_1"
        documentos={[
          { documento_id: "doc_1", pagina: 1, url: "/t1.webp" },
          { documento_id: "doc_2", pagina: 2, url: "/t2.webp" },
        ]}
        destinoInicial={{ documento_id: "doc_1", pagina: 1, n: 1 }}
      />,
    );
    const raiz = document.querySelector(".leque-leitor");
    expect(raiz).toHaveAttribute("data-leitor-aberto", "true");
    expect(raiz?.querySelector('[aria-label="Leque de documentos"]')).toBeNull();
  });

  it("actualização de destino abre o leitor após o leque já montado", async () => {
    const { rerender } = render(
      <LequeLeitor
        mensagemId="msg_1"
        chatId="cht_1"
        documentos={[{ documento_id: "doc_1", pagina: 1, url: "/t1.webp" }]}
      />,
    );
    expect(document.querySelector(".leque-leitor")).toHaveAttribute(
      "data-leitor-aberto",
      "false",
    );
    rerender(
      <LequeLeitor
        mensagemId="msg_1"
        chatId="cht_1"
        documentos={[{ documento_id: "doc_1", pagina: 1, url: "/t1.webp" }]}
        destinoInicial={{ documento_id: "doc_1", pagina: 2, n: 3 }}
      />,
    );
    expect(document.querySelector(".leque-leitor")).toHaveAttribute(
      "data-leitor-aberto",
      "true",
    );
  });
});
