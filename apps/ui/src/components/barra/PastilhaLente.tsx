import { copy } from "../../lib/copy";
import { LENTES, type LenteId } from "../../lib/lentes";

const ROTULO: Record<LenteId, string> = {
  investigar: copy.lens.investigate,
  assessment: copy.lens.assessment,
  acreditacao: copy.lens.accreditation,
  verificar: copy.lens.verify,
};

export type PastilhaLenteProps = {
  lente: LenteId;
  onMudar?: (lente: LenteId) => void;
};

export function PastilhaLente({ lente, onMudar }: PastilhaLenteProps) {
  return (
    <label className="pastilha pastilha-lente">
      <select
        aria-label="Lente de trabalho"
        value={lente}
        onChange={(e) => onMudar?.(e.target.value as LenteId)}
      >
        {LENTES.map((id) => (
          <option key={id} value={id}>
            {ROTULO[id]}
          </option>
        ))}
      </select>
    </label>
  );
}
