import { copy } from "../../lib/copy";

export type EntradaSumario = { titulo: string; pagina: number };

export type SumarioProps = {
  aberto: boolean;
  entradas: EntradaSumario[];
  onIr: (pagina: number) => void;
  onFechar: () => void;
};

export function Sumario({ aberto, entradas, onIr, onFechar }: SumarioProps) {
  if (!aberto) return null;
  return (
    <nav className="leitor-sumario vidro" aria-label={copy.reader.toc}>
      <header className="leitor-sumario__cab">
        <h2>{copy.reader.toc}</h2>
        <button type="button" className="botao-icone" onClick={onFechar}>
          {copy.chrome.close}
        </button>
      </header>
      <ul>
        {entradas.map((e) => (
          <li key={`${e.pagina}-${e.titulo}`}>
            <button type="button" onClick={() => onIr(e.pagina)}>
              {e.titulo}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}
