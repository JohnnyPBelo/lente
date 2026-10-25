import { LequeLeitor } from "../leque/LequeLeitor";
import type { MiniaturaDoc } from "../leque/Miniatura";

export type SlotLeitorProps = {
  mensagemId?: string;
  chatId?: string;
  miniaturas?: MiniaturaDoc[];
};

/** Sítio reservado no chrome para leque/leitor (PLN-15). */
export function SlotLeitor({
  mensagemId,
  chatId,
  miniaturas = [],
}: SlotLeitorProps) {
  return (
    <div data-slot="leitor" className="slot-leitor">
      {miniaturas.length ? (
        <LequeLeitor
          mensagemId={mensagemId}
          chatId={chatId}
          documentos={miniaturas}
        />
      ) : null}
    </div>
  );
}
