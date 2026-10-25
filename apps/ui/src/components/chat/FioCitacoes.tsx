import { CitacaoLink, type DestinoCitacao } from "./CitacaoLink";

export type LinhaFio = {
  id: string;
  texto: string;
  citacao?: DestinoCitacao;
};

export type FioCitacoesProps = {
  linhas: LinhaFio[];
  onAbrirCitacao: (destino: DestinoCitacao) => void;
};

/** Frases do fio como links activáveis (REG-DOS-001). */
export function FioCitacoes({ linhas, onAbrirCitacao }: FioCitacoesProps) {
  return (
    <div className="fio-citacoes" role="feed">
      {linhas.map((linha) =>
        linha.citacao ? (
          <CitacaoLink
            key={linha.id}
            n={linha.citacao.n}
            destino={linha.citacao}
            onAbrir={onAbrirCitacao}
          >
            {linha.texto}
          </CitacaoLink>
        ) : (
          <span key={linha.id}>{linha.texto}</span>
        ),
      )}
    </div>
  );
}
