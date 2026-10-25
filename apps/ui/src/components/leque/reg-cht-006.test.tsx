import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Leque } from "./Leque";

const docs = [
  { documento_id: "doc_a", pagina: 1, url: "/a.webp" },
  { documento_id: "doc_b", pagina: 2, url: "/b.webp" },
  { documento_id: "doc_c", pagina: 3, url: "/c.webp" },
];

describe("REG-CHT-006", () => {
  it("tacto: 1.º toque abre leque; 2.º numa miniatura abre o leitor", async () => {
    const u = userEvent.setup();
    const onAbrir = vi.fn();
    render(<Leque documentos={docs} onAbrir={onAbrir} tacto />);
    const root = document.querySelector(".leque")!;
    expect(root).toHaveAttribute("data-aberto", "false");
    fireEvent.touchStart(root);
    expect(root).toHaveClass("leque--aberto");
    expect(onAbrir).not.toHaveBeenCalled();
    await u.click(screen.getAllByRole("button")[1]!);
    expect(onAbrir).toHaveBeenCalledWith("doc_b");
  });
});
