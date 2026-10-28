import { LequeLeitor, type DestinoLeitor } from "../leque/LequeLeitor";
import type { MiniaturaDoc } from "../leque/Miniatura";

export type SlotLeitorProps = {
  mensagemId?: string;
  chatId?: string;
  miniaturas?: MiniaturaDoc[];
  /** Citação a abrir no leitor (issue #73). */
  destino?: DestinoLeitor | null;
};

/** Sítio reservado no chrome para leque/leitor (PLN-15). */
export function SlotLeitor({
  mensagemId,
  chatId,
  miniaturas = [],
  destino = null,
}: SlotLeitorProps) {
  return (
    <div data-slot="leitor" className="slot-leitor">
      {miniaturas.length ? (
        <LequeLeitor
          mensagemId={mensagemId}
          chatId={chatId}
          documentos={miniaturas}
          destinoInicial={destino}
        />
      ) : null}
    </div>
  );
}
