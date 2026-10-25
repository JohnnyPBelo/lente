import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Leque } from "./Leque";

const docs = [
  { documento_id: "a", pagina: 1, url: "/a.webp" },
  { documento_id: "b", pagina: 1, url: "/b.webp" },
];

describe("REG-CHT-007", () => {
  const original = window.matchMedia;

  afterEach(() => {
    window.matchMedia = original;
  });

  it("reduced-motion encurta animação sem remover leque nem abertura", async () => {
    const u = userEvent.setup();
    const onAbrir = vi.fn();
    window.matchMedia = ((query: string) =>
      ({
        matches: String(query).includes("prefers-reduced-motion: reduce"),
        media: query,
        onchange: null,
        addListener: () => {},
        removeListener: () => {},
        addEventListener: () => {},
        removeEventListener: () => {},
        dispatchEvent: () => false,
      })) as typeof window.matchMedia;

    render(<Leque documentos={docs} onAbrir={onAbrir} />);
    const root = document.querySelector(".leque")!;
    expect(root).toHaveAttribute("data-reduced-motion", "true");
    expect(root).toHaveAttribute("data-animacao", "curta");
    await u.hover(root);
    expect(root).toHaveClass("leque--aberto");
    await u.click(screen.getAllByRole("button")[0]!);
    expect(onAbrir).toHaveBeenCalledWith("a");
  });
});
