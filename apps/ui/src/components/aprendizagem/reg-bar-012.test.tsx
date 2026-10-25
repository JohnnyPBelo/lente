import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { copy, entradasMenuMais } from "../../lib/copy";

function MenuMais() {
  return (
    <ul aria-label={copy.bar.menu_hint}>
      {entradasMenuMais.map((rotulo) => (
        <li key={rotulo}>
          <button type="button">{rotulo}</button>
        </li>
      ))}
    </ul>
  );
}

describe("REG-BAR-012", () => {
  it("menu + / / não lista Exportar nem Importar correções", () => {
    render(<MenuMais />);
    const menu = screen.getByRole("list", { name: copy.bar.menu_hint });
    expect(menu).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: copy.learn.export }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: copy.learn.import }),
    ).not.toBeInTheDocument();
    for (const rotulo of entradasMenuMais) {
      expect(screen.getByRole("button", { name: rotulo })).toBeInTheDocument();
    }
    expect(entradasMenuMais).not.toContain(copy.learn.export);
    expect(entradasMenuMais).not.toContain(copy.learn.import);
  });
});
