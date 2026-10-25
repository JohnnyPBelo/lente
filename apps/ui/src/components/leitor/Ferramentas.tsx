import { useEffect, useState } from "react";
import { copy } from "../../lib/copy";

export type FerramentasProps = {
  pagina: number;
  total: number;
  zoom: number;
  onZoom: (z: number) => void;
  onAjustarLargura: () => void;
  onAjustarPagina: () => void;
  onIrPagina: (p: number) => void;
  onProcurar: (termo: string) => void;
  onSumario: () => void;
  onMinimizar: () => void;
  onMarcaSeguinte: () => void;
  onMarcaAnterior: () => void;
};

export function Ferramentas({
  pagina,
  total,
  zoom,
  onZoom,
  onAjustarLargura,
  onAjustarPagina,
  onIrPagina,
  onProcurar,
  onSumario,
  onMinimizar,
  onMarcaSeguinte,
  onMarcaAnterior,
}: FerramentasProps) {
  const [paginaRascunho, setPaginaRascunho] = useState(String(pagina));
  useEffect(() => {
    setPaginaRascunho(String(pagina));
  }, [pagina]);

  return (
    <div className="leitor-ferramentas vidro" role="toolbar" aria-label="Ferramentas do leitor">
      <button type="button" onClick={() => onZoom(zoom + 0.1)}>
        {copy.reader.zoom_in}
      </button>
      <button type="button" onClick={() => onZoom(Math.max(0.4, zoom - 0.1))}>
        {copy.reader.zoom_out}
      </button>
      <button type="button" onClick={onAjustarLargura}>
        {copy.reader.fit_width}
      </button>
      <button type="button" onClick={onAjustarPagina}>
        {copy.reader.fit_page}
      </button>
      <label>
        {copy.reader.goto_page}
        <input
          type="number"
          min={1}
          max={total}
          value={paginaRascunho}
          aria-label={copy.reader.goto_page}
          onChange={(e) => setPaginaRascunho(e.target.value)}
          onBlur={() => {
            const n = Number(paginaRascunho);
            onIrPagina(Number.isFinite(n) && n >= 1 ? n : 1);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              const n = Number(paginaRascunho);
              onIrPagina(Number.isFinite(n) && n >= 1 ? n : 1);
            }
          }}
        />
      </label>
      <span>
        {copy.reader.page_of
          .replace("{current}", String(pagina))
          .replace("{total}", String(total))}
      </span>
      <label>
        {copy.reader.find_in_doc}
        <input
          type="search"
          aria-label={copy.reader.find_in_doc}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              onProcurar((e.target as HTMLInputElement).value);
            }
          }}
        />
      </label>
      <button type="button" onClick={onSumario}>
        {copy.reader.toc}
      </button>
      <button type="button" onClick={onMarcaAnterior}>
        {copy.reader.prev_mark}
      </button>
      <button type="button" onClick={onMarcaSeguinte}>
        {copy.reader.next_mark}
      </button>
      <button type="button" onClick={onMinimizar}>
        {copy.reader.minimize}
      </button>
    </div>
  );
}
