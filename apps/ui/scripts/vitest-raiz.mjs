#!/usr/bin/env node
/**
 * O manifesto passa caminhos desde a raiz do repositório
 * (`apps/ui/src/...`), mas scripts/regressao.sh corre vitest com cwd em apps/ui.
 * Este bin local remapeia esses caminhos antes de delegar no Vitest real.
 */
import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import path from "node:path";

const require = createRequire(import.meta.url);
const aqui = path.dirname(fileURLToPath(import.meta.url));
const pacoteUi = path.resolve(aqui, "..");

const PREFIXO = "apps/ui/";
const args = process.argv.slice(2).map((arg) => {
  if (arg === PREFIXO.slice(0, -1) || arg === "apps/ui") {
    return "src";
  }
  if (arg.startsWith(PREFIXO)) {
    return arg.slice(PREFIXO.length);
  }
  return arg;
});

const vitestCli = require.resolve("vitest/vitest.mjs", { paths: [pacoteUi] });
const resultado = spawnSync(process.execPath, [vitestCli, ...args], {
  stdio: "inherit",
  cwd: pacoteUi,
  env: process.env,
});
process.exit(resultado.status ?? 1);
