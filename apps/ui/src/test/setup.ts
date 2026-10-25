import "@testing-library/jest-dom/vitest";
import { beforeEach } from "vitest";
import { reiniciarApiFalsa } from "../lib/api";

beforeEach(() => {
  reiniciarApiFalsa();
});
