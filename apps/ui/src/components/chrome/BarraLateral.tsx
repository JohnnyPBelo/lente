/** Stub — o chrome da barra lateral ainda não existe (PLN-13). */
export type ConversaLista = { id: string; nome: string };

export type BarraLateralProps = {
  conversas?: ConversaLista[];
  conversaActivaId?: string | null;
  onSeleccionar?: (id: string) => void;
};

export function BarraLateral(_props: BarraLateralProps) {
  return null;
}
