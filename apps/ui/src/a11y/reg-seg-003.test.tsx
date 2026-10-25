import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "../App";
import { reiniciarApiFalsa } from "../lib/api";

describe("REG-SEG-003", () => {
  it("a aplicação não expõe login, permissões partilhadas nem sincronização", () => {
    reiniciarApiFalsa();
    const { container } = render(<App />);
    const texto = container.textContent?.toLowerCase() ?? "";

    for (const termo of [
      "login",
      "iniciar sessão",
      "criar conta",
      "password",
      "palavra-passe",
      "sincronizar",
      "sincronização",
      "permissões partilhadas",
      "partilhar com",
      "oauth",
    ]) {
      expect(texto).not.toContain(termo);
    }

    expect(screen.queryByRole("button", { name: /login/i })).toBeNull();
    expect(screen.queryByRole("textbox", { name: /password|palavra-passe/i })).toBeNull();
  });
});
