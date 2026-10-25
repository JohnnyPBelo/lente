import { Mensagem } from "./Mensagem";
import { copy } from "../../lib/copy";
import type { MensagemFalsa } from "../../lib/api";

export type AreaChatProps = {
  mensagens?: MensagemFalsa[];
  vazia?: boolean;
};

export function AreaChat({ mensagens = [], vazia }: AreaChatProps) {
  const mostrarVazio = vazia ?? mensagens.length === 0;

  return (
    <section className="area-chat" aria-live="polite">
      {mostrarVazio ? (
        <div className="area-chat__vazio">
          <h1>{copy.chat.empty_title}</h1>
          <p>{copy.chat.empty_body}</p>
        </div>
      ) : (
        <div className="area-chat__fio">
          {mensagens.map((mensagem) => (
            <Mensagem key={mensagem.id} papel={mensagem.papel}>
              {mensagem.papel === "utilizador"
                ? mensagem.texto
                : (mensagem.frases?.join(" ") ?? mensagem.texto ?? "")}
            </Mensagem>
          ))}
        </div>
      )}
    </section>
  );
}
