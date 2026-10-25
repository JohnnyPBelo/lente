import { useEffect, useMemo, useRef, useState } from "react";
import { copy } from "../../lib/copy";
import {
  fixarTrecho,
  obterDocumento,
  obterHighlights,
  obterPagina,
  type DocumentoLeitor,
  type HighlightApi,
  type PaginaLeitor,
} from "../../lib/api";
import { Ferramentas } from "./Ferramentas";
import { Highlights, type HighlightMarca } from "./Highlights";
import { Sumario } from "./Sumario";

export type LeitorProps = {
  documentoId: string;
  mensagemId?: string;
  paginaInicial?: number;
  highlightN?: number | null;
  chatId?: string;
  aberto: boolean;
  onMinimizar: () => void;
  onConfrontarSelecao?: (
    texto: string,
    meta: { documento_id: string; pagina: number },
  ) => void;
  onCorrigirSelecao?: (positivo: string, negativos: string[]) => void;
  corrigirActivo?: boolean;
};

export function Leitor({
  documentoId,
  mensagemId,
  paginaInicial = 1,
  highlightN = null,
  chatId = "cht_01",
  aberto,
  onMinimizar,
  onConfrontarSelecao,
  onCorrigirSelecao,
  corrigirActivo = false,
}: LeitorProps) {
  const [doc, setDoc] = useState<DocumentoLeitor | null>(null);
  const [pagina, setPagina] = useState(paginaInicial);
  const [paginas, setPaginas] = useState<PaginaLeitor[]>([]);
  const [marcas, setMarcas] = useState<HighlightMarca[]>([]);
  const [zoom, setZoom] = useState(1);
  const [ajuste, setAjuste] = useState<"livre" | "largura" | "pagina">("livre");
  const [sumarioAberto, setSumarioAberto] = useState(false);
  const [aceso, setAceso] = useState<number | null>(highlightN);
  const [selecao, setSelecao] = useState("");
  const [ocorrencia, setOcorrencia] = useState<string | null>(null);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const refsPagina = useRef<Record<number, HTMLElement | null>>({});
  const superficieRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!aberto) return;
    let vivo = true;
    void (async () => {
      const d = await obterDocumento(documentoId);
      if (!vivo) return;
      setDoc(d);
      const hs = await obterHighlights(documentoId, mensagemId);
      if (!vivo) return;
      setMarcas(
        hs.map((h: HighlightApi) => ({
          n: h.n,
          pagina: h.pagina,
          offsets: h.offsets,
          caixas: h.caixas,
        })),
      );
      const carregadas: PaginaLeitor[] = [];
      for (let p = 1; p <= d.paginas; p += 1) {
        carregadas.push(await obterPagina(documentoId, p));
        if (!vivo) return;
      }
      setPaginas(carregadas);
    })();
    return () => {
      vivo = false;
    };
  }, [aberto, documentoId, mensagemId]);

  useEffect(() => {
    setPagina(paginaInicial);
  }, [paginaInicial, documentoId]);

  useEffect(() => {
    if (highlightN != null && aberto) {
      setAceso(highlightN);
      const t = window.setTimeout(() => setAceso(null), 800);
      return () => window.clearTimeout(t);
    }
  }, [highlightN, aberto]);

  useEffect(() => {
    function esc(ev: KeyboardEvent) {
      if (ev.key === "Escape" && aberto) {
        ev.preventDefault();
        onMinimizar();
      }
    }
    window.addEventListener("keydown", esc);
    return () => window.removeEventListener("keydown", esc);
  }, [aberto, onMinimizar]);

  useEffect(() => {
    const el = refsPagina.current[pagina];
    if (el && typeof el.scrollIntoView === "function") {
      el.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
  }, [pagina, paginas.length]);

  const total = doc?.paginas ?? 1;
  const tipo = doc?.tipo ?? "texto";
  const textoPaginaActual =
    paginas.find((p) => p.pagina === pagina)?.texto ?? "";

  const estiloVista = useMemo(() => {
    const base: import("react").CSSProperties = {
      transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
      transformOrigin: "top left",
    };
    if (ajuste === "largura") {
      return { ...base, width: "100%", maxWidth: "100%" };
    }
    if (ajuste === "pagina") {
      return { ...base, height: "100%" };
    }
    return base;
  }, [zoom, ajuste, pan]);

  if (!aberto) {
    return null;
  }

  function aoSeleccionar() {
    const sel = window.getSelection()?.toString() ?? "";
    setSelecao(sel);
    if (corrigirActivo && sel && onCorrigirSelecao) {
      const negativos = marcas.map((m) => {
        const txt =
          paginas.find((p) => p.pagina === m.pagina)?.texto ?? textoPaginaActual;
        return txt.slice(m.offsets.inicio, m.offsets.fim);
      });
      onCorrigirSelecao(sel, negativos);
    }
  }

  async function copiar(texto?: string) {
    const t = texto || selecao || window.getSelection()?.toString() || "";
    if (t && navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(t);
    }
  }

  async function copiarCitacao(texto?: string) {
    const t = texto || selecao || window.getSelection()?.toString() || "";
    const ficheiro = doc?.titulo ?? documentoId;
    const formatado = `${ficheiro}, p. ${pagina}: «${t}»`;
    await navigator.clipboard.writeText(formatado);
  }

  async function fixar() {
    const t = selecao || window.getSelection()?.toString() || "";
    if (!t) return;
    await fixarTrecho(chatId, {
      documento_id: documentoId,
      pagina,
      texto: t,
      offsets: { inicio: 0, fim: t.length },
    });
  }

  function saltoMarca(dir: 1 | -1) {
    if (!marcas.length) return;
    const ord = [...marcas].sort(
      (a, b) => a.pagina - b.pagina || a.offsets.inicio - b.offsets.inicio,
    );
    let idx = ord.findIndex((m) => m.n === aceso);
    if (idx < 0) {
      idx = ord.findIndex((m) => m.pagina === pagina);
      if (idx < 0) {
        idx = dir > 0 ? -1 : 0;
      }
    }
    const prox = ord[(idx + dir + ord.length) % ord.length]!;
    setPagina(prox.pagina);
    setAceso(prox.n);
  }

  function procurarNeste(termo: string) {
    const q = termo.toLowerCase();
    for (const p of paginas) {
      if (p.texto.toLowerCase().includes(q)) {
        setPagina(p.pagina);
        setOcorrencia(termo);
        return;
      }
    }
    setOcorrencia(null);
  }

  return (
    <div
      className="leitor"
      data-slot="leitor"
      data-tipo={tipo}
      data-serif="true"
      data-animacao="curta"
      role="dialog"
      aria-label={doc?.titulo ?? copy.a11y.reader}
    >
      <Ferramentas
        pagina={pagina}
        total={total}
        zoom={zoom}
        onZoom={(z) => {
          setAjuste("livre");
          setZoom(z);
        }}
        onAjustarLargura={() => setAjuste("largura")}
        onAjustarPagina={() => setAjuste("pagina")}
        onIrPagina={setPagina}
        onProcurar={procurarNeste}
        onSumario={() => setSumarioAberto(true)}
        onMinimizar={onMinimizar}
        onMarcaSeguinte={() => saltoMarca(1)}
        onMarcaAnterior={() => saltoMarca(-1)}
      />
      <Sumario
        aberto={sumarioAberto}
        entradas={doc?.sumario ?? []}
        onIr={(p) => {
          setPagina(p);
          setSumarioAberto(false);
        }}
        onFechar={() => setSumarioAberto(false)}
      />
      <div
        ref={superficieRef}
        className="leitor-superficie"
        data-superficie="solida"
        data-scroll="continuo"
        onMouseUp={aoSeleccionar}
        onMouseDown={(e) => {
          if (tipo === "imagem" || tipo === "pdf") {
            const ox = e.clientX - pan.x;
            const oy = e.clientY - pan.y;
            function move(ev: MouseEvent) {
              setPan({ x: ev.clientX - ox, y: ev.clientY - oy });
            }
            function up() {
              window.removeEventListener("mousemove", move);
              window.removeEventListener("mouseup", up);
            }
            window.addEventListener("mousemove", move);
            window.addEventListener("mouseup", up);
          }
        }}
      >
        <div className="leitor-vista" style={estiloVista} data-ajuste={ajuste}>
          {paginas.map((p) => (
            <section
              key={p.pagina}
              className="leitor-pagina"
              data-pagina={p.pagina}
              ref={(el) => {
                refsPagina.current[p.pagina] = el;
              }}
            >
              <Highlights
                marcas={marcas}
                textoPagina={p.texto}
                pagina={p.pagina}
                acesoN={aceso}
              />
            </section>
          ))}
          {ocorrencia ? (
            <p className="leitor-ocorrencia" role="status">
              {ocorrencia}
            </p>
          ) : null}
        </div>
      </div>
      {selecao ? (
        <div className="leitor-bolha vidro" role="toolbar">
          <button type="button" onClick={() => void copiar(selecao)}>
            {copy.reader.copy}
          </button>
          <button type="button" onClick={() => void copiarCitacao(selecao)}>
            {copy.reader.copy_citation}
          </button>
          <button type="button" onClick={() => void fixar()}>
            {copy.reader.pin_excerpt}
          </button>
          <button
            type="button"
            onClick={() =>
              onConfrontarSelecao?.(selecao, {
                documento_id: documentoId,
                pagina,
              })
            }
          >
            {copy.reader.bubble_confront}
          </button>
        </div>
      ) : null}
    </div>
  );
}
