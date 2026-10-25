import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Leque } from "./Leque";

const tres = [
  { documento_id: "doc_1", pagina: 1, url: "/t1.webp" },
  { documento_id: "doc_2", pagina: 2, url: "/t2.webp" },
  { documento_id: "doc_3", pagina: 3, url: "/t3.webp" },
];

describe("REG-CHT-004", () => {
  it("um documento: clique na miniatura abre o leitor", async () => {
    const u = userEvent.setup();
    const onAbrir = vi.fn();
    render(
      <Leque
        documentos={[{ documento_id: "doc_unico", pagina: 1, url: "/u.webp" }]}
        onAbrir={onAbrir}
      />,
    );
    expect(document.querySelector(".leque--unico")).toBeTruthy();
    await u.click(screen.getByRole("button"));
    expect(onAbrir).toHaveBeenCalledWith("doc_unico");
  });

  it("três miniaturas: hover/foco revela leque; clique na 2.ª chama onAbrir", async () => {
    const u = userEvent.setup();
    const onAbrir = vi.fn();
    render(<Leque documentos={tres} onAbrir={onAbrir} />);
    const root = document.querySelector(".leque")!;
    expect(root).toHaveAttribute("data-aberto", "false");
    await u.hover(root);
    expect(root).toHaveClass("leque--aberto");
    expect(root).toHaveAttribute("data-aberto", "true");
    const botoes = screen.getAllByRole("button");
    await u.click(botoes[1]!);
    expect(onAbrir).toHaveBeenCalledWith("doc_2");
  });

  it("prefers-reduced-motion: animações curtas mas leque e abertura disponíveis", async () => {
    const u = userEvent.setup();
    const onAbrir = vi.fn();
    const original = window.matchMedia;
    window.matchMedia = ((query: string) =>
      ({
        matches: query.includes("prefers-reduced-motion") && query.includes("reduce"),
        media: query,
        onchange: null,
        addListener: () => {},
        removeListener: () => {},
        addEventListener: () => {},
        removeEventListener: () => {},
        dispatchEvent: () => false,
      })) as typeof window.matchMedia;
    render(<Leque documentos={tres} onAbrir={onAbrir} />);
    const root = document.querySelector(".leque")!;
    expect(root).toHaveAttribute("data-reduced-motion", "true");
    expect(root).toHaveAttribute("data-animacao", "curta");
    await u.hover(root);
    expect(root).toHaveClass("leque--aberto");
    await u.click(screen.getAllByRole("button")[1]!);
    expect(onAbrir).toHaveBeenCalledWith("doc_2");
    window.matchMedia = original;
  });
});
