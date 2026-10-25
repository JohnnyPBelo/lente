import { useCallback, useEffect, useState } from "react";
import { copy } from "../../lib/copy";
import { Leitor, type LeitorProps } from "../leitor/Leitor";
import { Leque, type LequeProps } from "./Leque";
import type { MiniaturaDoc } from "./Miniatura";

export type DestinoLeitor = {
  documento_id: string;
  pagina: number;
  n: number;
};

export type LequeLeitorProps = {
  mensagemId?: string;
  chatId?: string;
  documentos: MiniaturaDoc[];
  destinoInicial?: DestinoLeitor | null;
  tacto?: boolean;
  corrigirActivo?: boolean;
  onConfrontarSelecao?: LeitorProps["onConfrontarSelecao"];
  onCorrigirSelecao?: LeitorProps["onCorrigirSelecao"];
  /** Abre o leitor numa citação sem passar pelo leque. */
  onRegistarAbrirCitacao?: (abrir: (d: DestinoLeitor) => void) => void;
};

/** Leque → leitor com recolha à miniatura (PLN-15). */
export function LequeLeitor({
  mensagemId,
  chatId = "cht_01",
  documentos,
  destinoInicial = null,
  tacto = false,
  corrigirActivo = false,
  onConfrontarSelecao,
  onCorrigirSelecao,
  onRegistarAbrirCitacao,
}: LequeLeitorProps) {
  const [leitorAberto, setLeitorAberto] = useState(Boolean(destinoInicial));
  const [docActivo, setDocActivo] = useState<string | null>(
    destinoInicial?.documento_id ?? null,
  );
  const [pagina, setPagina] = useState(destinoInicial?.pagina ?? 1);
  const [highlightN, setHighlightN] = useState<number | null>(
    destinoInicial?.n ?? null,
  );

  const abrirDocumento = useCallback(
    (documentoId: string, pag = 1, n: number | null = null) => {
      setDocActivo(documentoId);
      setPagina(pag);
      setHighlightN(n);
      setLeitorAberto(true);
    },
    [],
  );

  const abrirCitacao = useCallback(
    (destino: DestinoLeitor) => {
      abrirDocumento(destino.documento_id, destino.pagina, destino.n);
    },
    [abrirDocumento],
  );

  useEffect(() => {
    onRegistarAbrirCitacao?.(abrirCitacao);
  }, [abrirCitacao, onRegistarAbrirCitacao]);

  const minimizar = useCallback(() => {
    setLeitorAberto(false);
    setHighlightN(null);
  }, []);

  const lequeProps: LequeProps = {
    documentos,
    tacto,
    onAbrir: (id) => {
      const doc = documentos.find((d) => d.documento_id === id);
      abrirDocumento(id, doc?.pagina ?? 1, null);
    },
  };

  return (
    <div
      className="leque-leitor"
      data-slot="leitor"
      data-leitor-aberto={leitorAberto ? "true" : "false"}
      aria-label={copy.a11y.reader}
    >
      {!leitorAberto ? (
        <div aria-label={copy.a11y.fan}>
          <Leque {...lequeProps} />
        </div>
      ) : null}
      {docActivo ? (
        <Leitor
          documentoId={docActivo}
          mensagemId={mensagemId}
          paginaInicial={pagina}
          highlightN={highlightN}
          chatId={chatId}
          aberto={leitorAberto}
          onMinimizar={minimizar}
          corrigirActivo={corrigirActivo}
          onConfrontarSelecao={onConfrontarSelecao}
          onCorrigirSelecao={onCorrigirSelecao}
        />
      ) : null}
    </div>
  );
}
