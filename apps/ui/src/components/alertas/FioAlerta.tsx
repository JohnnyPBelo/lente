import { copy } from "../../lib/copy";

export type MensagemAlertaUi = {
  id: string;
  texto: string;
  documento_id?: string;
  miniatura?: string | null;
};

export type FioAlertaProps = {
  alertaId: string;
  titulo: string;
  activo: boolean;
  mensagens?: MensagemAlertaUi[];
  onAlternar?: (activo: boolean) => void;
};

/**
 * Fio próprio de um alerta com interruptor no topo.
 */
export function FioAlerta({
  alertaId,
  titulo,
  activo,
  mensagens = [],
  onAlternar,
}: FioAlertaProps) {
  const rotulo = activo ? copy.alerts.toggle_on : copy.alerts.toggle_off;

  return (
    <article aria-label={titulo} data-alerta-id={alertaId}>
      <header>
        <h1>{titulo}</h1>
        <button
          type="button"
          role="switch"
          aria-checked={activo}
          aria-label={rotulo}
          onClick={() => onAlternar?.(!activo)}
        >
          {rotulo}
        </button>
      </header>
      <ol>
        {mensagens.map((m) => (
          <li key={m.id}>
            <p>{m.texto}</p>
            {m.miniatura ? (
              <img
                src={m.miniatura}
                alt={`Miniatura do documento ${m.documento_id}`}
                data-documento={m.documento_id}
              />
            ) : null}
          </li>
        ))}
      </ol>
    </article>
  );
}
