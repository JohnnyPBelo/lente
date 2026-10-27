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
  const rotulo =
    doc.titulo ??
    `Documento ${doc.documento_id}, página ${doc.pagina}`;
  const alt = doc.titulo
    ? `Miniatura: ${doc.titulo}`
    : `Miniatura do documento ${doc.documento_id}, página ${doc.pagina}`;

  return (
    <button
      type="button"
      className={
        seleccionada ? "miniatura miniatura--activa" : "miniatura"
      }
      data-documento-id={doc.documento_id}
      data-fonte="indexacao"
      data-pagina={doc.pagina}
      aria-label={rotulo}
      onMouseEnter={onFoco}
      onFocus={onFoco}
      onClick={() => onAbrir?.(doc.documento_id)}
    >
      <img src={doc.url} alt={alt} className="miniatura__img" draggable={false} />
    </button>
  );
}
