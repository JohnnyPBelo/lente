export type MiniaturaDoc = {
  documento_id: string;
  pagina: number;
  url: string;
  titulo?: string;
};

export type MiniaturaProps = {
  doc: MiniaturaDoc;
  seleccionada?: boolean;
  onAbrir?: (documentoId: string) => void;
  onFoco?: () => void;
};

export function Miniatura({
  doc,
  seleccionada = false,
  onAbrir,
  onFoco,
}: MiniaturaProps) {
  return (
    <button
      type="button"
      className={
        seleccionada ? "miniatura miniatura--activa" : "miniatura"
      }
      data-documento-id={doc.documento_id}
      data-fonte="indexacao"
      data-pagina={doc.pagina}
      aria-label={doc.titulo ?? `Documento ${doc.documento_id}, página ${doc.pagina}`}
      onMouseEnter={onFoco}
      onFocus={onFoco}
      onClick={() => onAbrir?.(doc.documento_id)}
    >
      <img src={doc.url} alt="" className="miniatura__img" draggable={false} />
    </button>
  );
}
