import { copy } from "../../lib/copy";
import { Leque } from "../leque/Leque";
import type { MiniaturaDoc } from "../leque/Miniatura";
import { CitacaoLink, type DestinoCitacao } from "./CitacaoLink";

export type ExcertoCorrelacao = {
  n: number;
  papel: "A" | "B" | "relacao";
  documento_id: string;
  pagina: number;
  texto: string;
};

export type FraseComCitacao = {
  texto: string;
  n: number;
  destino: DestinoCitacao;
};

export type MensagemComDocumentosProps = {
  miniaturas: MiniaturaDoc[];
  onAbrirDoc: (documentoId: string) => void;
  onAbrirCitacao: (destino: DestinoCitacao) => void;
  correlacionar?: boolean;
  excertos?: ExcertoCorrelacao[];
  frases?: FraseComCitacao[];
};

/** Resposta com citações, correlacionar ou leque (PLN-15). */
export function MensagemComDocumentos({
  miniaturas,
  onAbrirDoc,
  onAbrirCitacao,
  correlacionar = false,
  excertos = [],
  frases = [],
}: MensagemComDocumentosProps) {
  return (
    <div className="mensagem-docs" data-animacao="entrada">
      {correlacionar ? (
        <>
          <ul className="correlacao-legendas" aria-label="Legendas">
            <li>{copy.correlate.legend_a}</li>
            <li>{copy.correlate.legend_b}</li>
            <li>{copy.correlate.legend_relation}</li>
          </ul>
          {excertos.map((ex) => (
            <p
              key={`${ex.papel}-${ex.n}`}
              data-papel={ex.papel}
              className={`correlacao-papel-${ex.papel === "relacao" ? "relacao" : ex.papel.toLowerCase()}`}
            >
              {ex.texto}
            </p>
          ))}
        </>
      ) : null}
      {frases.map((frase) => (
        <p key={frase.n} className="mensagem-docs__frase">
          {frase.texto}{" "}
          <CitacaoLink n={frase.n} destino={frase.destino} onAbrir={onAbrirCitacao} />
        </p>
      ))}
      {miniaturas.length ? (
        <Leque documentos={miniaturas} onAbrir={onAbrirDoc} />
      ) : null}
    </div>
  );
}
