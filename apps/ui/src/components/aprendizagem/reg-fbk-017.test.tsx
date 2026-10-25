import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { copy, entradasMenuMais } from "../../lib/copy";
import { EstadoAprendizagem } from "./EstadoAprendizagem";

function BarraLateralComAprendizagem() {
  return (
    <nav aria-label={copy.a11y.sidebar}>
      <EstadoAprendizagem />
      <ul aria-label={copy.bar.menu_hint}>
        {entradasMenuMais.map((rotulo) => (
          <li key={rotulo}>
            <button type="button">{rotulo}</button>
          </li>
        ))}
      </ul>
    </nav>
  );
}

describe("REG-FBK-017", () => {
  it("Exportar/Importar estão no topo da aprendizagem, não no menu +", () => {
    render(<BarraLateralComAprendizagem />);

    const aprendizagem = screen.getByTestId("estado-aprendizagem");
    expect(aprendizagem).toHaveTextContent(copy.learn.group);
    expect(
      screen.getByRole("button", { name: copy.learn.export }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: copy.learn.import }),
    ).toBeInTheDocument();

    const menu = screen.getByRole("list", { name: copy.bar.menu_hint });
    expect(menu.textContent).not.toContain(copy.learn.export);
    expect(menu.textContent).not.toContain(copy.learn.import);
  });
});
