import { describe, expect, it } from "vitest";
import { copy } from "../../lib/copy";
import { MODOS } from "../../lib/lentes";
import { ROTULO_MODO } from "./MenuMais";

describe("REG-SEG-006", () => {
  it("nenhum modo é playbook ofensivo nem geração de ataque", () => {
    const textos = [
      ...MODOS.map((m) => ROTULO_MODO[m]),
      copy.mode.search,
      copy.bar.menu_hint,
      JSON.stringify(copy),
    ].join(" ").toLowerCase();
    expect(textos).not.toMatch(/playbook|procedimento de ataque|offensive|exploit kit/);
    expect(MODOS).not.toContain("ataque" as never);
  });
});
