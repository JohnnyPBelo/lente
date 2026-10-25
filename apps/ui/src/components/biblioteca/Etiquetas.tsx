import { useState, type FormEvent } from "react";
import { copy } from "../../lib/copy";

export type EtiquetasProps = {
  documentoId: string;
  etiquetas: string[];
  onAlterar?: (documentoId: string, etiquetas: string[]) => void;
};

/** Etiquetas manuais de um documento — copy de lib.tags. */
export function Etiquetas({
  documentoId,
  etiquetas,
  onAlterar,
}: EtiquetasProps) {
  const [rascunho, setRascunho] = useState("");
  const [lista, setLista] = useState<string[]>(etiquetas);

  function acrescentar(evento: FormEvent) {
    evento.preventDefault();
    const nome = rascunho.trim();
    if (!nome || lista.includes(nome)) {
      setRascunho("");
      return;
    }
    const seguinte = [...lista, nome];
    setLista(seguinte);
    setRascunho("");
    onAlterar?.(documentoId, seguinte);
  }

  function remover(nome: string) {
    const seguinte = lista.filter((e) => e !== nome);
    setLista(seguinte);
    onAlterar?.(documentoId, seguinte);
  }

  return (
    <div aria-label={copy.lib.tags} data-testid="etiquetas">
      <span>{copy.lib.tags}</span>
      <ul role="list">
        {lista.map((nome) => (
          <li key={nome}>
            <span>{nome}</span>
            <button
              type="button"
              aria-label={`Remover ${nome}`}
              onClick={() => remover(nome)}
            >
              {copy.chrome.close}
            </button>
          </li>
        ))}
      </ul>
      <form onSubmit={acrescentar}>
        <label>
          {copy.lib.tags}
          <input
            value={rascunho}
            onChange={(e) => setRascunho(e.target.value)}
            aria-label={copy.lib.tags}
          />
        </label>
        <button type="submit">{copy.chrome.confirm}</button>
      </form>
    </div>
  );
}
