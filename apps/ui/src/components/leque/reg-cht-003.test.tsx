import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Leque } from "./Leque";

describe("REG-CHT-003", () => {
  it("miniatura por documento na página do primeiro highlight (URL da indexação)", () => {
    render(
      <Leque
        documentos={[
          { documento_id: "doc_a", pagina: 4, url: "/media/thumbs/doc_a_p4.webp" },
          { documento_id: "doc_b", pagina: 1, url: "/media/thumbs/doc_b_p1.webp" },
        ]}
        onAbrir={vi.fn()}
      />,
    );
    const imgs = document.querySelectorAll("img.miniatura__img");
    expect(imgs).toHaveLength(2);
    expect(imgs[0]).toHaveAttribute("src", "/media/thumbs/doc_a_p4.webp");
    expect(imgs[1]).toHaveAttribute("src", "/media/thumbs/doc_b_p1.webp");
    expect(document.querySelector('[data-documento-id="doc_a"]')).toHaveAttribute(
      "data-fonte",
      "indexacao",
    );
  });
});
