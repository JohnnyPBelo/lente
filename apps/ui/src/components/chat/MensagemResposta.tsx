import { useRef } from "react";
import { Mensagem } from "../chrome/Mensagem";
import { LequeLeitor, type DestinoLeitor } from "../leque/LequeLeitor";
import type { MiniaturaDoc } from "../leque/Miniatura";
import { CitacaoLink, type DestinoCitacao } from "./CitacaoLink";
import { LinhaFeedback } from "./LinhaFeedback";

export type FraseCitada = {
  texto: string;
  citacao?: DestinoCitacao;
};

export type MensagemRespostaProps = {
  mensagemId: string;
  chatId?: string;
  frases: FraseCitada[];
  miniaturas: MiniaturaDoc[];
  tacto?: boolean;
};

/** Prosa com links de citação, leque e leitor (PLN-15). */
export function MensagemResposta({
  mensagemId,
  chatId,
  frases,
  miniaturas,
  tacto = false,
}: MensagemRespostaProps) {
  const abrirCitacaoRef = useRef<((d: DestinoLeitor) => void) | null>(null);

  function aoCitacao(destino: DestinoCitacao) {
    abrirCitacaoRef.current?.({
      documento_id: destino.documento_id,
      pagina: destino.pagina,
      n: destino.n,
    });
  }

  return (
    <Mensagem papel="assistente">
      <div className="mensagem-resposta" data-mensagem-id={mensagemId}>
        {frases.map((frase, i) => (
          <p key={`${mensagemId}-f-${i}`} className="mensagem-resposta__frase">
            {frase.texto}{" "}
            {frase.citacao ? (
              <CitacaoLink
                n={frase.citacao.n}
                destino={frase.citacao}
                onAbrir={aoCitacao}
              />
            ) : null}
          </p>
        ))}
        <LinhaFeedback
          mensagemId={mensagemId}
          temHighlights={frases.some((f) => Boolean(f.citacao)) || miniaturas.length > 0}
        />
        <LequeLeitor
          mensagemId={mensagemId}
          chatId={chatId}
          documentos={miniaturas}
          tacto={tacto}
          onRegistarAbrirCitacao={(fn) => {
            abrirCitacaoRef.current = fn;
          }}
        />
      </div>
    </Mensagem>
  );
}
