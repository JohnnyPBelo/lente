import { useCallback, useEffect, useRef, useState } from "react";
import {
  ErroIngestao,
  ingerirFicheiro,
  ingerirUrl,
  listarBiblioteca,
} from "../../lib/api";
import { copy } from "../../lib/copy";
import { BibliotecaVazia } from "../vazios/BibliotecaVazia";
import { UrlRecusada } from "../vazios/UrlRecusada";
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
  const [urlRecusada, setUrlRecusada] = useState(false);
  const [url, setUrl] = useState("");
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
    setUrlRecusada(false);
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

  async function aoUrl(e: React.FormEvent) {
    e.preventDefault();
    const alvo = url.trim();
    if (!alvo) return;
    setACarregar(true);
    setErro(null);
    setUrlRecusada(false);
    try {
      const r = await ingerirUrl(alvo);
      onIngerido?.(r.documento_id);
      setUrl("");
      await refrescar();
    } catch (err) {
      if (err instanceof ErroIngestao && err.codigo === "url_privada") {
        setUrlRecusada(true);
      } else {
        setErro(err instanceof Error ? err.message : "Falha na ingestão");
      }
    } finally {
      setACarregar(false);
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
        <form className="painel-biblioteca__url" onSubmit={(ev) => void aoUrl(ev)}>
          <label className="visually-hidden" htmlFor="biblioteca-url">
            {copy.lib.add_url}
          </label>
          <input
            id="biblioteca-url"
            type="url"
            inputMode="url"
            placeholder={copy.lib.url_placeholder}
            value={url}
            disabled={aCarregar}
            onChange={(e) => setUrl(e.target.value)}
          />
          <button type="submit" className="botao-fantasma" disabled={aCarregar || !url.trim()}>
            {copy.lib.add_url}
          </button>
        </form>
      </header>
      {urlRecusada ? <UrlRecusada /> : null}
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
