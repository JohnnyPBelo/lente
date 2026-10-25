/**
 * Vista read-only da fotografia do dossier.
 * Links de citação expõem página/caixas para o leitor (PLN-15 liga o destino).
 * Copy: docs/interface/copy.md → chat.dossier.*
 */

import { copy } from "../../lib/copy";

export type CaixaProva = {
  pagina: number;
  x: number;
  y: number;
  largura: number;
  altura: number;
};

export type FraseDossier = {
  indice?: number;
  texto?: string;
  frase_resposta?: string;
  trecho?: string;
  trecho_literal?: string;
  ficheiro?: string;
  pagina: number;
  offset_inicio?: number;
  offset_fim?: number;
  caixas?: CaixaProva[];
  pontuacao_juiz?: number;
  score_juiz?: number;
};

export type VistaDossierProps = {
  titulo?: string;
  fonteAlterada?: boolean;
  frases: FraseDossier[];
  onAbrirProva?: (frase: FraseDossier) => void;
};

export function VistaDossier({
  titulo,
  fonteAlterada = false,
  frases,
  onAbrirProva,
}: VistaDossierProps) {
  return (
    <article className="vista-dossier" aria-label={copy.chat.dossier.reopen}>
      {titulo ? <h2 className="vista-dossier__titulo">{titulo}</h2> : null}
      {fonteAlterada ? (
        <p className="vista-dossier__aviso" role="status">
          {copy.chat.dossier.source_changed}
        </p>
      ) : null}
      <ul className="vista-dossier__frases">
        {frases.map((frase, i) => {
          const rotulo =
            frase.frase_resposta ??
            frase.texto ??
            frase.trecho_literal ??
            frase.trecho ??
            `Citação ${frase.indice ?? i + 1}`;
          const caixasJson = JSON.stringify(frase.caixas ?? []);
          return (
            <li key={`${frase.indice ?? i}-${frase.pagina}`}>
              <button
                type="button"
                className="vista-dossier__citacao"
                data-pagina={frase.pagina}
                data-offset-inicio={frase.offset_inicio ?? 0}
                data-offset-fim={frase.offset_fim ?? 0}
                data-caixas={caixasJson}
                data-ficheiro={frase.ficheiro ?? ""}
                aria-label={`${copy.chat.open_source}: ${rotulo}`}
                onClick={() => onAbrirProva?.(frase)}
              >
                {rotulo}
              </button>
            </li>
          );
        })}
      </ul>
    </article>
  );
}
