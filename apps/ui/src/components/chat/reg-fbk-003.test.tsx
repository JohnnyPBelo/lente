import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { copy } from "../../lib/copy";
import { LinhaFeedback } from "./LinhaFeedback";

describe("REG-FBK-003", () => {
  it("link Corrigir mais tarde abre o fluxo Corrigir", async () => {
    const user = userEvent.setup();
    render(<LinhaFeedback mensagemId="msg_2" temHighlights />);
    await user.click(screen.getByRole("button", { name: copy.feedback.dismiss }));
    const link = screen.getByRole("button", { name: copy.feedback.fix_later });
    expect(link).toBeInTheDocument();
    await user.click(link);
    expect(screen.getByTestId("fluxo-corrigir")).toHaveTextContent(copy.feedback.fix);
  });
});
