import { useCallback, useEffect, useRef, useState } from "react";
import { ingerirFicheiro, listarBiblioteca } from "../../lib/api";
import { copy } from "../../lib/copy";
import { BibliotecaVazia } from "../vazios/BibliotecaVazia";
import { ListaVirtualizada, type DocumentoLista } from "./ListaVirtualizada";

export type PainelBibliotecaProps = {
  onFechar?: () => void;
  onIngerido?: (documentoId: string) => void;
};

export function PainelBiblioteca({
  onFechar,
  onIngerido,
}: PainelBibliotecaProps) {
  const [docs, setDocs] = useState<DocumentoLista[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [aCarregar, setACarregar] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const refrescar = useCallback(async () => {
    try {
      const itens = await listarBiblioteca();
      setDocs(
        itens.map((d) => ({
          id: d.id,
          titulo: d.titulo,
          etiquetas: d.etiquetas,
          desactualizado: d.desactualizado,
          tipo: d.tipo_sugerido ?? undefined,
        })),
      );
      setErro(null);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Falha a listar a biblioteca");
    }
  }, []);

  useEffect(() => {
    void refrescar();
  }, [refrescar]);

  async function aoFicheiro(lista: FileList | null) {
    if (!lista?.length) return;
    setACarregar(true);
    setErro(null);
    try {
      for (const ficheiro of Array.from(lista)) {
        const r = await ingerirFicheiro(ficheiro);
        onIngerido?.(r.documento_id);
      }
      await refrescar();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Falha na ingestão");
    } finally {
      setACarregar(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  function abrirEscolha() {
    inputRef.current?.click();
  }

  return (
    <section
      className="painel-biblioteca vidro"
      aria-label={copy.lib.title}
      data-slot="biblioteca"
    >
      <header className="painel-biblioteca__cabecalho">
        <h2>{copy.lib.title}</h2>
        <div className="painel-biblioteca__acoes">
          <button
            type="button"
            className="botao-primario"
            disabled={aCarregar}
            onClick={abrirEscolha}
          >
            {copy.lib.add}
          </button>
          {onFechar ? (
            <button type="button" className="botao-fantasma" onClick={onFechar}>
              {copy.chrome.cancel}
            </button>
          ) : null}
        </div>
        <input
          ref={inputRef}
          type="file"
          accept=".md,.markdown,.txt,.docx,.pdf,image/*"
          multiple
          hidden
          onChange={(e) => void aoFicheiro(e.target.files)}
        />
      </header>
      {erro ? (
        <p role="alert" className="painel-biblioteca__erro">
          {erro}
        </p>
      ) : null}
      {docs.length === 0 ? (
        <BibliotecaVazia onAcrescentar={abrirEscolha} />
      ) : (
        <ListaVirtualizada documentos={docs} />
      )}
    </section>
  );
}
