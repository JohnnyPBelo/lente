import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { copy } from "../../lib/copy";
import { LinhaFeedback } from "./LinhaFeedback";

describe("REG-FBK-001", () => {
  it("mostra Acertou, Corrigir e Descartar; outra procura não espera", async () => {
    const user = userEvent.setup();
    const onProcura = vi.fn();
    render(
      <div>
        <LinhaFeedback mensagemId="msg_1" temHighlights />
        <button type="button" onClick={onProcura}>
          Nova procura
        </button>
      </div>,
    );
    expect(screen.getByRole("button", { name: copy.feedback.hit })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: copy.feedback.fix })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: copy.feedback.dismiss })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Nova procura" }));
    expect(onProcura).toHaveBeenCalledTimes(1);
    // Feedback ainda disponível — não bloqueou
    expect(screen.getByRole("button", { name: copy.feedback.hit })).toBeInTheDocument();
  });
});
