import { copy } from "../../lib/copy";

export type AlertaLista = {
  id: string;
  texto: string;
  activo: boolean;
  chat_id: string;
};

export type GrupoAlertasProps = {
  alertas: AlertaLista[];
  alertaActivoId?: string | null;
  onSeleccionar?: (id: string) => void;
};

/**
 * Grupo «Alertas» da barra lateral — por baixo das conversas.
 * PLN-19; a barra de modos/lentes fica no PLN-14.
 */
export function GrupoAlertas({
  alertas,
  alertaActivoId = null,
  onSeleccionar,
}: GrupoAlertasProps) {
  if (alertas.length === 0) {
    return null;
  }

  return (
    <section aria-label={copy.alerts.group}>
      <h2>{copy.alerts.group}</h2>
      <ul role="list" aria-label={copy.alerts.group}>
        {alertas.map((alerta) => {
          const seleccionado = alerta.id === alertaActivoId;
          return (
            <li key={alerta.id}>
              <button
                type="button"
                aria-current={seleccionado ? "true" : undefined}
                onClick={() => onSeleccionar?.(alerta.id)}
              >
                {alerta.texto}
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
