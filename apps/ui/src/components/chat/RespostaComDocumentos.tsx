import { useCallback, useState } from "react";
import { Leitor } from "../leitor/Leitor";
import {
  MensagemComDocumentos,
  type MensagemComDocumentosProps,
} from "./MensagemComDocumentos";
import type { DestinoCitacao } from "./CitacaoLink";

export type RespostaComDocumentosProps = Omit<
  MensagemComDocumentosProps,
  "onAbrirDoc" | "onAbrirCitacao"
> & {
  chatId?: string;
  mensagemId?: string;
  onConfrontarSelecao?: (
    texto: string,
    meta: { documento_id: string; pagina: number },
  ) => void;
  onCorrigirSelecao?: (positivo: string, negativos: string[]) => void;
  corrigirActivo?: boolean;
};

/**
 * Mensagem com miniaturas/leque e leitor ligado — cresce a partir da
 * miniatura escolhida ou de uma citação; Escape/minimizar recolhe.
 */
export function RespostaComDocumentos({
  chatId = "cht_01",
  mensagemId,
  onConfrontarSelecao,
  onCorrigirSelecao,
  corrigirActivo,
  ...msg
}: RespostaComDocumentosProps) {
  const [aberto, setAberto] = useState(false);
  const [docId, setDocId] = useState<string | null>(null);
  const [pagina, setPagina] = useState(1);
  const [highlightN, setHighlightN] = useState<number | null>(null);

  const abrirDoc = useCallback((id: string) => {
    setDocId(id);
    setPagina(1);
    setHighlightN(null);
    setAberto(true);
  }, []);

  const abrirCitacao = useCallback((destino: DestinoCitacao) => {
    setDocId(destino.documento_id);
    setPagina(destino.pagina);
    setHighlightN(destino.n);
    setAberto(true);
  }, []);

  const minimizar = useCallback(() => {
    setAberto(false);
  }, []);

  return (
    <div className="resposta-docs" data-leitor-aberto={aberto ? "true" : "false"}>
      <MensagemComDocumentos
        {...msg}
        onAbrirDoc={abrirDoc}
        onAbrirCitacao={abrirCitacao}
      />
      {docId ? (
        <Leitor
          aberto={aberto}
          documentoId={docId}
          mensagemId={mensagemId}
          paginaInicial={pagina}
          highlightN={highlightN}
          chatId={chatId}
          onMinimizar={minimizar}
          onConfrontarSelecao={onConfrontarSelecao}
          onCorrigirSelecao={onCorrigirSelecao}
          corrigirActivo={corrigirActivo}
        />
      ) : null}
    </div>
  );
}
