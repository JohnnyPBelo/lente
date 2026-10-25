import { Mensagem } from "./Mensagem";
import type { MensagemFalsa } from "../../lib/api";
import { ConversaNova } from "../vazios/ConversaNova";

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
          <ConversaNova />
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
