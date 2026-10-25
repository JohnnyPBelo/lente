import { copy } from "../../lib/copy";

export type DestinoCitacao = {
  documento_id: string;
  pagina: number;
  n: number;
  offsets?: { inicio: number; fim: number };
};

export type CitacaoLinkProps = {
  n: number;
  destino: DestinoCitacao;
  onAbrir: (destino: DestinoCitacao) => void;
  children?: React.ReactNode;
};

export function CitacaoLink({ n, destino, onAbrir, children }: CitacaoLinkProps) {
  const rotulo = copy.chat.citation.replace("{n}", String(n));
  return (
    <button
      type="button"
      className="citacao-link"
      data-documento-id={destino.documento_id}
      data-pagina={destino.pagina}
      data-n={n}
      aria-label={`${copy.chat.open_source} [${n}]`}
      onClick={() => onAbrir(destino)}
    >
      {children ?? rotulo}
    </button>
  );
}
