export type HighlightMarca = {
  n: number;
  pagina: number;
  offsets: { inicio: number; fim: number };
  caixas?: { pagina: number; x: number; y: number; w: number; h: number }[];
};

export type HighlightsProps = {
  marcas: HighlightMarca[];
  textoPagina: string;
  pagina: number;
  acesoN?: number | null;
};

/** Highlight = intervalo literal dos offsets (não regenera texto). */
export function Highlights({
  marcas,
  textoPagina,
  pagina,
  acesoN = null,
}: HighlightsProps) {
  const naPagina = marcas.filter((m) => m.pagina === pagina);
  if (!naPagina.length) {
    return <span className="leitor-texto">{textoPagina}</span>;
  }

  const partes: import("react").ReactNode[] = [];
  let cursor = 0;
  const ordenadas = [...naPagina].sort(
    (a, b) => a.offsets.inicio - b.offsets.inicio,
  );
  for (const m of ordenadas) {
    const ini = Math.max(0, Math.min(textoPagina.length, m.offsets.inicio));
    const fim = Math.max(ini, Math.min(textoPagina.length, m.offsets.fim));
    if (cursor < ini) {
      partes.push(textoPagina.slice(cursor, ini));
    }
    const pedaco = textoPagina.slice(ini, fim);
    partes.push(
      <mark
        key={`h-${m.n}-${ini}`}
        className={
          acesoN === m.n ? "highlight highlight--aceso" : "highlight"
        }
        data-n={m.n}
        data-inicio={ini}
        data-fim={fim}
        data-literal="true"
      >
        {pedaco}
      </mark>,
    );
    cursor = fim;
  }
  if (cursor < textoPagina.length) {
    partes.push(textoPagina.slice(cursor));
  }
  return <span className="leitor-texto">{partes}</span>;
}
