import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { copy } from "../../lib/copy";
import {
  CHAVE_ONBOARDING_JA_VI,
  deveMostrarOnboarding,
  gravarJaVi,
  limparJaVi,
} from "../../lib/onboarding";
import { Onboarding } from "./Onboarding";

function memoriaStorage(): Storage {
  const mapa = new Map<string, string>();
  return {
    get length() {
      return mapa.size;
    },
    clear() {
      mapa.clear();
    },
    getItem(chave: string) {
      return mapa.has(chave) ? mapa.get(chave)! : null;
    },
    key(indice: number) {
      return [...mapa.keys()][indice] ?? null;
    },
    removeItem(chave: string) {
      mapa.delete(chave);
    },
    setItem(chave: string, valor: string) {
      mapa.set(chave, String(valor));
    },
  };
}

describe("onboarding primeiro uso", () => {
  let store: Storage;

  beforeEach(() => {
    store = memoriaStorage();
    limparJaVi(store);
  });

  it("mostra a introdução quando ainda não há «já vi»", () => {
    expect(deveMostrarOnboarding({ armazenamento: store })).toBe(true);
    render(
      <Onboarding
        armazenamento={store}
        estadosModelos={{ embedding: "pronto", juiz: "pronto", escritor: "ausente" }}
      />,
    );
    expect(screen.getByTestId("onboarding")).toBeInTheDocument();
    expect(screen.getByRole("dialog")).toHaveAccessibleName(copy.onboarding.title);
    expect(screen.getByText(copy.onboarding.passos.procura.titulo)).toBeInTheDocument();
  });

  it("não mostra quando «já vi» está gravado", () => {
    gravarJaVi(store);
    expect(deveMostrarOnboarding({ armazenamento: store })).toBe(false);
    render(<Onboarding armazenamento={store} />);
    expect(screen.queryByTestId("onboarding")).not.toBeInTheDocument();
  });

  it("«Já vi» dispensa e persiste", async () => {
    const user = userEvent.setup();
    render(<Onboarding armazenamento={store} />);
    expect(screen.getByTestId("onboarding")).toBeInTheDocument();
    await user.click(screen.getByTestId("onboarding-ja-vi"));
    expect(screen.queryByTestId("onboarding")).not.toBeInTheDocument();
    expect(store.getItem(CHAVE_ONBOARDING_JA_VI)).toBe("1");
  });

  it("Escape dispensa como «Já vi»", async () => {
    const user = userEvent.setup();
    render(<Onboarding armazenamento={store} />);
    await user.keyboard("{Escape}");
    expect(screen.queryByTestId("onboarding")).not.toBeInTheDocument();
    expect(store.getItem(CHAVE_ONBOARDING_JA_VI)).toBe("1");
  });

  it("?onboarding=1 força a introdução mesmo com «já vi»", () => {
    gravarJaVi(store);
    expect(
      deveMostrarOnboarding({ armazenamento: store, pesquisa: "?onboarding=1" }),
    ).toBe(true);
    render(<Onboarding armazenamento={store} pesquisa="?onboarding=1" />);
    expect(screen.getByTestId("onboarding")).toBeInTheDocument();
  });

  it("passo modelos distingue pronto e ausente", async () => {
    const user = userEvent.setup();
    render(
      <Onboarding
        armazenamento={store}
        estadosModelos={{
          embedding: "pronto",
          juiz: "ausente",
          escritor: "ausente",
        }}
      />,
    );
    // Avançar até modelos (último passo).
    const seguinte = screen.getByRole("button", { name: copy.onboarding.seguinte });
    for (let i = 0; i < 11; i += 1) {
      await user.click(seguinte);
    }
    expect(screen.getByTestId("onboarding")).toHaveAttribute("data-passo", "modelos");
    const lista = screen.getByTestId("onboarding-modelos");
    expect(lista.querySelector('[data-estado="pronto"]')).toHaveTextContent(
      copy.onboarding.passos.modelos.pronto,
    );
    expect(lista.querySelectorAll('[data-estado="ausente"]')).toHaveLength(2);
  });
});
