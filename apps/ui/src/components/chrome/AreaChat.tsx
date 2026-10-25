import type { ReactNode } from "react";
import { Mensagem } from "./Mensagem";
import type { MensagemFalsa } from "../../lib/api";
import { ConversaNova } from "../vazios/ConversaNova";
import { ProcuraSemDocumentos } from "../vazios/ProcuraSemDocumentos";

export type AreaChatProps = {
  mensagens?: MensagemFalsa[];
  vazia?: boolean;
  /** Última procura sem excertos/frases — estado vazio canónico. */
  procuraVazia?: boolean;
  renderAssistente?: (mensagem: MensagemFalsa) => ReactNode;
};

export function AreaChat({
  mensagens = [],
  vazia,
  procuraVazia = false,
  renderAssistente,
}: AreaChatProps) {
  const mostrarVazio = vazia ?? mensagens.length === 0;

  return (
    <section className="area-chat" aria-live="polite">
      {mostrarVazio ? (
        <div className="area-chat__vazio">
          <ConversaNova />
        </div>
      ) : (
        <div className="area-chat__fio">
          {mensagens.map((mensagem) => {
            if (mensagem.papel === "utilizador") {
              return (
                <Mensagem key={mensagem.id} papel="utilizador">
                  {mensagem.texto}
                </Mensagem>
              );
            }
            const custom = renderAssistente?.(mensagem);
            if (custom != null) {
              return (
                <Mensagem key={mensagem.id} papel="assistente">
                  {custom}
                </Mensagem>
              );
            }
            const texto =
              mensagem.frases?.join(" ") ?? mensagem.texto ?? "";
            const semProva =
              !texto &&
              !(mensagem.excertos && mensagem.excertos.length) &&
              !(mensagem.miniaturas && mensagem.miniaturas.length);
            return (
              <Mensagem key={mensagem.id} papel="assistente">
                {semProva ? <ProcuraSemDocumentos /> : texto}
              </Mensagem>
            );
          })}
          {procuraVazia ? (
            <div className="area-chat__vazio-inline">
              <ProcuraSemDocumentos />
            </div>
          ) : null}
        </div>
      )}
    </section>
  );
}
