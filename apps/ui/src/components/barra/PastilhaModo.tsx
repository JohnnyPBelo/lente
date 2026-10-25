import { copy } from "../../lib/copy";
import type { ModoId } from "../../lib/lentes";

const ROTULO: Record<Exclude<ModoId, "procurar">, string> = {
  correlacionar: copy.mode.correlate,
  confrontar: copy.mode.confront,
  alerta: copy.mode.alert,
  lacunas: copy.mode.gaps,
};

export type PastilhaModoProps = {
  modo: ModoId;
};

export function PastilhaModo({ modo }: PastilhaModoProps) {
  if (modo === "procurar") {
    return null;
  }
  return (
    <span className="pastilha pastilha-modo" data-modo={modo} role="status">
      {ROTULO[modo]}
    </span>
  );
}
