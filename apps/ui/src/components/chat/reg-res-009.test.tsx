import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { reiniciarApiFalsa, semearDocumento, listarFixadosFalsos } from "../../lib/api";

import { CitacaoLink } from "./CitacaoLink";

describe("REG-RES-009", () => {
  it("clique na citação abre página e highlight", async () => {
    const onAbrir = vi.fn();
    const user = userEvent.setup();
    render(
      <CitacaoLink
        n={2}
        destino={{ documento_id: "doc_9", pagina: 4, n: 2, offsets: { inicio: 10, fim: 20 } }}
        onAbrir={onAbrir}
      />,
    );
    await user.click(screen.getByRole("button"));
    expect(onAbrir).toHaveBeenCalledWith(
      expect.objectContaining({ documento_id: "doc_9", pagina: 4, n: 2 }),
    );
  });
});
