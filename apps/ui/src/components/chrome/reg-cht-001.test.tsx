import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa } from "../../lib/api";
import { BarraLateral } from "./BarraLateral";

describe("REG-CHT-001", () => {
  beforeEach(() => {
    reiniciarApiFalsa();
  });

  it("renderiza Nova conversa e mostra o nome da lista", () => {
    render(
      <BarraLateral
        conversas={[{ id: "cht_01", nome: "Quem aprova o acesso remoto?" }]}
      />,
    );

    expect(
      screen.getByRole("navigation", { name: copy.a11y.sidebar }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: copy.chrome.new_chat }),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Quem aprova o acesso remoto?"),
    ).toBeInTheDocument();
  });

  it("cria, renomeia e apaga uma conversa na lista", async () => {
    const utilizador = userEvent.setup();
    render(<BarraLateral conversas={[]} />);

    await utilizador.click(
      screen.getByRole("button", { name: copy.chrome.new_chat }),
    );

    const lista = screen.getByRole("list", { name: copy.conversations.group });
    const itens = within(lista).getAllByRole("listitem");
    expect(itens).toHaveLength(1);

    const item = itens[0]!;
    const menu = within(item).getByRole("button", { name: "Menu da conversa" });
    await utilizador.click(menu);
    await utilizador.click(
      screen.getByRole("menuitem", { name: copy.chrome.rename }),
    );

    const campo = screen.getByRole("textbox", { name: copy.chrome.rename });
    await utilizador.clear(campo);
    await utilizador.type(campo, "Acesso remoto");
    await utilizador.click(
      screen.getByRole("button", { name: copy.chrome.confirm }),
    );

    expect(within(lista).getByText("Acesso remoto")).toBeInTheDocument();

    await utilizador.click(
      within(lista)
        .getByRole("listitem")
        .querySelector('button[aria-label="Menu da conversa"]')!,
    );
    await utilizador.click(
      screen.getByRole("menuitem", { name: copy.chrome.delete }),
    );

    expect(within(lista).queryAllByRole("listitem")).toHaveLength(0);
  });
});
