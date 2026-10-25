import { copy } from "../../lib/copy";
import { Leque } from "../leque/Leque";
import type { MiniaturaDoc } from "../leque/Miniatura";

export type EventoCorrelacao = {
  papel: "A" | "B" | "relacao";
  texto: string;
  documento_id: string;
  pagina: number;
};

export type MensagemCorrelacaoProps = {
  conceitoA: string;
  conceitoB: string;
  eventos: EventoCorrelacao[];
  miniaturas: MiniaturaDoc[];
  onAbrirDocumento: (documentoId: string) => void;
};

/** Resposta de correlacionar: três cores + leque (REG-BUS-011). */
export function MensagemCorrelacao({
  conceitoA,
  conceitoB,
  eventos,
  miniaturas,
  onAbrirDocumento,
}: MensagemCorrelacaoProps) {
  return (
    <article className="mensagem-correlacao" data-mensagem="correlacionar">
      <ul className="correlacao-legendas" aria-label="Legendas">
        <li className="correlacao-papel-a">{copy.correlate.legend_a}</li>
        <li className="correlacao-papel-b">{copy.correlate.legend_b}</li>
        <li className="correlacao-papel-relacao">
          {copy.correlate.legend_relation}
        </li>
      </ul>
      <p>
        <span className="sr-only">{copy.bar.correlate_a}</span>
        <strong className="correlacao-papel-a">{conceitoA}</strong>
        {" · "}
        <span className="sr-only">{copy.bar.correlate_b}</span>
        <strong className="correlacao-papel-b">{conceitoB}</strong>
      </p>
      <div className="correlacao-eventos">
        {eventos.map((ev) => (
          <p
            key={`${ev.papel}-${ev.documento_id}`}
            className={`correlacao-papel-${ev.papel === "relacao" ? "relacao" : ev.papel.toLowerCase()}`}
            data-papel={ev.papel}
          >
            {ev.texto}
          </p>
        ))}
      </div>
      <Leque documentos={miniaturas} onAbrir={onAbrirDocumento} />
    </article>
  );
}
