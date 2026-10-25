import { describe, expect, it } from "vitest";
import { copy } from "../../lib/copy";
import { LENTES, MODOS } from "../../lib/lentes";
import { ROTULO_MODO } from "./MenuMais";

describe("REG-FOR-010", () => {
  it("só os cinco modos e quatro lentes; sem ataque", () => {
    expect([...MODOS]).toEqual([
      "procurar",
      "correlacionar",
      "confrontar",
      "alerta",
      "lacunas",
    ]);
    expect(MODOS.map((m) => ROTULO_MODO[m])).toEqual([
      copy.mode.search,
      copy.mode.correlate,
      copy.mode.confront,
      copy.mode.alert,
      copy.mode.gaps,
    ]);
    expect([...LENTES]).toEqual([
      "investigar",
      "assessment",
      "acreditacao",
      "verificar",
    ]);
    expect(MODOS.join(" ")).not.toMatch(/ataque|attack/);
  });
});
