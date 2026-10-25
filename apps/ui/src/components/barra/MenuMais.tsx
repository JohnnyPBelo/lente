import { copy } from "../../lib/copy";
import { MODOS, type ModoId } from "../../lib/lentes";

const ROTULO: Record<ModoId, string> = {
  procurar: copy.mode.search,
  correlacionar: copy.mode.correlate,
  confrontar: copy.mode.confront,
  alerta: copy.mode.alert,
  lacunas: copy.mode.gaps,
};

export type MenuMaisProps = {
  aberto: boolean;
  activo: number;
  onSeleccionar: (modo: ModoId) => void;
};

export function MenuMais({ aberto, activo, onSeleccionar }: MenuMaisProps) {
  if (!aberto) {
    return null;
  }
  return (
    <ul
      className="menu-mais vidro"
      role="menu"
      aria-label={copy.bar.menu_hint}
    >
      {MODOS.map((modo, i) => (
        <li key={modo} role="none">
          <button
            type="button"
            role="menuitem"
            className={i === activo ? "menu-mais__item activo" : "menu-mais__item"}
            aria-current={i === activo ? "true" : undefined}
            onClick={() => onSeleccionar(modo)}
          >
            {ROTULO[modo]}
          </button>
        </li>
      ))}
    </ul>
  );
}

export { MODOS, ROTULO as ROTULO_MODO };
