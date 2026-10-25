import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const raizUi = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

/**
 * Contrato do artefacto que engine/api/estaticos.py monta (apps/ui/dist).
 * O build corre à parte; aqui validamos a entrada e, se dist existir, o index.
 */
describe("build estático para o motor", () => {
  it("index.html expõe #raiz para a app React", () => {
    const html = readFileSync(path.join(raizUi, "index.html"), "utf8");
    expect(html).toContain('id="raiz"');
    expect(html).toContain("/src/main.tsx");
  });

  it("após build, dist/index.html existe e referencia os assets", () => {
    const distIndex = path.join(raizUi, "dist", "index.html");
    if (!existsSync(distIndex)) {
      // Em CI da regressão o Vitest não corre o build; o commit de smoke corre npm run build antes.
      expect(existsSync(path.join(raizUi, "index.html"))).toBe(true);
      return;
    }
    const html = readFileSync(distIndex, "utf8");
    expect(html).toContain('id="raiz"');
    expect(html).toMatch(/assets\/index-.*\.js/);
  });
});
