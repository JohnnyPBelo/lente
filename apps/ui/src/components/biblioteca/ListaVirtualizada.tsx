import { useCallback, useMemo, useRef, useState } from "react";
import { copy } from "../../lib/copy";

export type DocumentoLista = {
  id: string;
  titulo: string;
  etiquetas?: string[];
  desactualizado?: boolean;
  tipo?: string;
};

export type ListaVirtualizadaProps = {
  documentos: DocumentoLista[];
  alturaLinha?: number;
  alturaViewport?: number;
  sobrejanela?: number;
  onSeleccionar?: (id: string) => void;
};

/**
 * Lista virtualizada da biblioteca: só monta a janela visível.
 * Sem dependência externa — janela por scrollTop / altura de linha.
 */
export function ListaVirtualizada({
  documentos,
  alturaLinha = 36,
  alturaViewport = 360,
  sobrejanela = 4,
  onSeleccionar,
}: ListaVirtualizadaProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [scrollTop, setScrollTop] = useState(0);

  const aoScroll = useCallback(() => {
    const el = ref.current;
    if (!el) {
      return;
    }
    setScrollTop(el.scrollTop);
  }, []);

  const { inicio, fim, offset } = useMemo(() => {
    const primeiro = Math.max(0, Math.floor(scrollTop / alturaLinha) - sobrejanela);
    const visiveis = Math.ceil(alturaViewport / alturaLinha) + sobrejanela * 2;
    const ultimo = Math.min(documentos.length, primeiro + visiveis);
    return {
      inicio: primeiro,
      fim: ultimo,
      offset: primeiro * alturaLinha,
    };
  }, [scrollTop, alturaLinha, alturaViewport, sobrejanela, documentos.length]);

  const fatia = documentos.slice(inicio, fim);
  const alturaTotal = documentos.length * alturaLinha;

  return (
    <section aria-label={copy.lib.title}>
      <div
        ref={ref}
        role="list"
        data-testid="lista-biblioteca"
        data-montados={fatia.length}
        data-total={documentos.length}
        onScroll={aoScroll}
        style={{
          height: alturaViewport,
          overflow: "auto",
          position: "relative",
        }}
      >
        <div style={{ height: alturaTotal, position: "relative" }}>
          <div
            style={{
              position: "absolute",
              top: offset,
              left: 0,
              right: 0,
            }}
          >
            {fatia.map((doc) => (
              <div
                key={doc.id}
                role="listitem"
                data-testid="linha-biblioteca"
                data-doc-id={doc.id}
                style={{
                  height: alturaLinha,
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  padding: "0 0.75rem",
                  boxSizing: "border-box",
                }}
              >
                <button
                  type="button"
                  onClick={() => onSeleccionar?.(doc.id)}
                  style={{
                    background: "none",
                    border: "none",
                    color: "inherit",
                    font: "inherit",
                    cursor: "pointer",
                    textAlign: "left",
                    flex: 1,
                  }}
                >
                  {doc.titulo}
                </button>
                {doc.desactualizado ? (
                  <span data-testid="estado-desactualizado">
                    {copy.lib.outdated}
                  </span>
                ) : null}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
