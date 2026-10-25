import { useState } from "react";
import { copy } from "../../lib/copy";

export type LinhaFeedbackProps = {
  mensagemId: string;
  /** Highlights sujeitos a feedback; sem isto a linha não aparece. */
  temHighlights?: boolean;
  onAcertou?: () => void;
  onCorrigir?: () => void;
  onDescartar?: () => void;
  onCorrigirMaisTarde?: () => void;
};

/**
 * Linha discreta Acertou / Corrigir / Descartar (REG-FBK-001)
 * e link «Corrigir mais tarde» (REG-FBK-003). Não bloqueia a procura seguinte.
 */
export function LinhaFeedback({
  mensagemId,
  temHighlights = true,
  onAcertou,
  onCorrigir,
  onDescartar,
  onCorrigirMaisTarde,
}: LinhaFeedbackProps) {
  const [descartado, setDescartado] = useState(false);
  const [corrigirAberto, setCorrigirAberto] = useState(false);

  if (!temHighlights) {
    return null;
  }

  function descartar() {
    setDescartado(true);
    onDescartar?.();
  }

  function corrigirAgora() {
    setCorrigirAberto(true);
    setDescartado(false);
    onCorrigir?.();
  }

  function corrigirMaisTarde() {
    setCorrigirAberto(true);
    onCorrigirMaisTarde?.();
  }

  return (
    <div
      className="linha-feedback"
      data-mensagem-id={mensagemId}
      data-testid="linha-feedback"
    >
      {!descartado && !corrigirAberto ? (
        <div className="linha-feedback__acoes" role="group" aria-label="Feedback">
          <button type="button" className="botao-fantasma" onClick={() => onAcertou?.()}>
            {copy.feedback.hit}
          </button>
          <button type="button" className="botao-fantasma" onClick={corrigirAgora}>
            {copy.feedback.fix}
          </button>
          <button type="button" className="botao-fantasma" onClick={descartar}>
            {copy.feedback.dismiss}
          </button>
        </div>
      ) : null}
      {(descartado || !corrigirAberto) && (
        <button
          type="button"
          className="linha-feedback__mais-tarde botao-fantasma"
          onClick={corrigirMaisTarde}
        >
          {copy.feedback.fix_later}
        </button>
      )}
      {corrigirAberto ? (
        <p className="linha-feedback__fluxo" data-testid="fluxo-corrigir">
          {copy.feedback.fix}
        </p>
      ) : null}
    </div>
  );
}
