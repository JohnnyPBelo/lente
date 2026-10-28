import { enviarFeedback } from "../../lib/api";
import { copy } from "../../lib/copy";
import { Leque } from "../leque/Leque";
import type { MiniaturaDoc } from "../leque/Miniatura";
import { CitacaoLink, type DestinoCitacao } from "./CitacaoLink";
import { LinhaFeedback } from "./LinhaFeedback";

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
  /** Sem destino (ex. lacuna «ausente») → sem link «Abrir na página». */
  destino?: DestinoCitacao | null;
};

export type MensagemComDocumentosProps = {
  miniaturas: MiniaturaDoc[];
  onAbrirDoc: (documentoId: string) => void;
  onAbrirCitacao: (destino: DestinoCitacao) => void;
  correlacionar?: boolean;
  excertos?: ExcertoCorrelacao[];
  frases?: FraseComCitacao[];
  /** Id da mensagem no fio — liga a linha de feedback (issue #58). */
  mensagemId?: string;
};

/** Resposta com citações, correlacionar ou leque (PLN-15). */
export function MensagemComDocumentos({
  miniaturas,
  onAbrirDoc,
  onAbrirCitacao,
  correlacionar = false,
  excertos = [],
  frases = [],
  mensagemId,
}: MensagemComDocumentosProps) {
  const temHighlights =
    frases.length > 0 || miniaturas.length > 0 || excertos.length > 0;
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
          {frase.texto}
          {frase.destino?.documento_id ? (
            <>
              {" "}
              <CitacaoLink
                n={frase.n}
                destino={frase.destino}
                onAbrir={onAbrirCitacao}
              />
            </>
          ) : null}
        </p>
      ))}
      {mensagemId ? (
        <LinhaFeedback
          mensagemId={mensagemId}
          temHighlights={temHighlights}
          onAcertou={() => {
            void enviarFeedback(mensagemId, "acertou");
          }}
          onDescartar={() => {
            void enviarFeedback(mensagemId, "descartar");
          }}
          onCorrigir={() => {
            /* fluxo Corrigir continua no leitor; registo via selecção */
          }}
        />
      ) : null}
      {miniaturas.length ? (
        <Leque documentos={miniaturas} onAbrir={onAbrirDoc} />
      ) : null}
    </div>
  );
}
