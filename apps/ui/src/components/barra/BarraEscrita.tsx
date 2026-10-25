import {
  useCallback,
  useEffect,
  useId,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent,
} from "react";
import { copy } from "../../lib/copy";
import {
  MODOS,
  type LenteId,
  type ModoId,
} from "../../lib/lentes";
import {
  correlacionar,
  confrontar,
  criarAlerta,
  lacunas,
  obterLimiar,
  procurar,
  type ResultadoProcura,
} from "../../lib/api";
import { MenuMais } from "./MenuMais";
import { PastilhaLente } from "./PastilhaLente";
import { PastilhaModo } from "./PastilhaModo";
import { Alerta } from "./modos/Alerta";
import { Confrontar, type TrechoBarra } from "./modos/Confrontar";
import { Correlacionar } from "./modos/Correlacionar";
import { Lacunas } from "./modos/Lacunas";
import { Procurar } from "./modos/Procurar";

export type ResultadoBarra =
  | {
      tipo: "procurar";
      texto: string;
      lente: LenteId;
      limiar: number;
      resposta: ResultadoProcura;
    }
  | {
      tipo: "correlacionar";
      conceito_a: string;
      conceito_b: string;
      lente: LenteId;
      resposta: Awaited<ReturnType<typeof correlacionar>>;
    }
  | {
      tipo: "confrontar";
      resposta: Awaited<ReturnType<typeof confrontar>>;
    }
  | { tipo: "alerta"; ok: boolean; erro?: string }
  | {
      tipo: "lacunas";
      resposta: Awaited<ReturnType<typeof lacunas>>;
    };

export type BarraEscritaProps = {
  chatId?: string;
  onResultado?: (r: ResultadoBarra) => void;
  onAbrirCitacao?: (doc: {
    documento_id: string;
    pagina: number;
  }) => void;
  /** Preenche o primeiro lugar vazio de Confrontar (bolha do leitor, PLN-15). */
  trechoConfrontarExterno?: TrechoBarra | null;
};

const VAZIO: TrechoBarra = { texto: "" };

export function BarraEscrita({
  chatId = "cht_01",
  onResultado,
  onAbrirCitacao,
  trechoConfrontarExterno = null,
}: BarraEscritaProps) {
  const baseId = useId();
  const rootRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const [modo, setModo] = useState<ModoId>("procurar");
  const [lente, setLente] = useState<LenteId>("investigar");
  const [menuAberto, setMenuAberto] = useState(false);
  const [indiceMenu, setIndiceMenu] = useState(0);

  const [texto, setTexto] = useState("");
  const [conceitoA, setConceitoA] = useState("");
  const [conceitoB, setConceitoB] = useState("");
  const [trechoA, setTrechoA] = useState<TrechoBarra>(VAZIO);
  const [trechoB, setTrechoB] = useState<TrechoBarra>(VAZIO);
  const [aEscolher, setAEscolher] = useState<"a" | "b" | null>(null);
  const [lacunasTexto, setLacunasTexto] = useState("");
  const [erroAlerta, setErroAlerta] = useState<string | null>(null);
  const [limiar, setLimiar] = useState<number | null>(null);

  const voltarProcurar = useCallback(() => {
    setMenuAberto(false);
    setModo("procurar");
    setAEscolher(null);
    setErroAlerta(null);
  }, []);

  const abrirMenu = useCallback(() => {
    setMenuAberto(true);
    setIndiceMenu(MODOS.indexOf(modo) >= 0 ? MODOS.indexOf(modo) : 0);
  }, [modo]);

  const seleccionarModo = useCallback((m: ModoId) => {
    setModo(m);
    setMenuAberto(false);
    setErroAlerta(null);
  }, []);

  useEffect(() => {
    if (!trechoConfrontarExterno?.texto) {
      return;
    }
    setModo("confrontar");
    setTrechoA((a) => {
      if (!a.texto.trim()) {
        return { ...trechoConfrontarExterno };
      }
      setTrechoB((b) => (b.texto.trim() ? b : { ...trechoConfrontarExterno }));
      return a;
    });
    const area = rootRef.current?.querySelector("textarea");
    area?.focus();
  }, [trechoConfrontarExterno]);

  useEffect(() => {
    function emEscape(ev: KeyboardEvent) {
      if (ev.key !== "Escape") {
        return;
      }
      if (menuAberto || modo !== "procurar") {
        ev.preventDefault();
        voltarProcurar();
      }
    }
    window.addEventListener("keydown", emEscape);
    return () => window.removeEventListener("keydown", emEscape);
  }, [menuAberto, modo, voltarProcurar]);

  useEffect(() => {
    let vivo = true;
    obterLimiar().then((v) => {
      if (vivo) {
        setLimiar(v);
      }
    });
    return () => {
      vivo = false;
    };
  }, []);

  async function enviar() {
    if (modo === "procurar") {
      const t = texto.trim();
      if (!t) return;
      const lim = limiar ?? (await obterLimiar());
      const resposta = await procurar({ chat_id: chatId, texto: t, lente });
      onResultado?.({
        tipo: "procurar",
        texto: t,
        lente,
        limiar: lim,
        resposta,
      });
      setTexto("");
      return;
    }
    if (modo === "correlacionar") {
      if (!conceitoA.trim() || !conceitoB.trim()) return;
      const resposta = await correlacionar({
        chat_id: chatId,
        conceito_a: conceitoA.trim(),
        conceito_b: conceitoB.trim(),
        lente,
      });
      onResultado?.({
        tipo: "correlacionar",
        conceito_a: conceitoA.trim(),
        conceito_b: conceitoB.trim(),
        lente,
        resposta,
      });
      return;
    }
    if (modo === "confrontar") {
      if (!trechoA.texto.trim() || !trechoB.texto.trim()) return;
      const resposta = await confrontar({
        chat_id: chatId,
        trecho_a: trechoA,
        trecho_b: trechoB,
      });
      onResultado?.({ tipo: "confrontar", resposta });
      return;
    }
    if (modo === "alerta") {
      const t = texto.trim();
      if (!t) return;
      const r = await criarAlerta({ texto: t, lente });
      if ("erro" in r && r.erro === "limite_alertas") {
        setErroAlerta(copy.alerts.limit);
        onResultado?.({ tipo: "alerta", ok: false, erro: copy.alerts.limit });
        return;
      }
      setErroAlerta(null);
      setTexto("");
      onResultado?.({ tipo: "alerta", ok: true });
      return;
    }
    if (modo === "lacunas") {
      const linhas = lacunasTexto
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean);
      if (!linhas.length) return;
      const resposta = await lacunas({
        chat_id: chatId,
        linhas,
        lente,
      });
      onResultado?.({ tipo: "lacunas", resposta });
    }
  }

  function tecladoBarra(e: ReactKeyboardEvent<HTMLDivElement>) {
    if (menuAberto) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setIndiceMenu((i) => (i + 1) % MODOS.length);
        return;
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        setIndiceMenu((i) => (i - 1 + MODOS.length) % MODOS.length);
        return;
      }
      if (e.key === "Enter") {
        e.preventDefault();
        seleccionarModo(MODOS[indiceMenu]!);
        return;
      }
      if (e.key === "Escape") {
        e.preventDefault();
        voltarProcurar();
        return;
      }
    } else if (e.key === "Escape" && modo !== "procurar") {
      e.preventDefault();
      voltarProcurar();
    }
  }

  function teclaCampo(e: ReactKeyboardEvent<HTMLDivElement>) {
    const alvo = e.target as HTMLElement;
    const emCampo =
      alvo.tagName === "INPUT" || alvo.tagName === "TEXTAREA";
    if (
      !menuAberto &&
      emCampo &&
      e.key === "/" &&
      (alvo as HTMLInputElement).value === "" &&
      !(alvo instanceof HTMLTextAreaElement && modo === "lacunas")
    ) {
      e.preventDefault();
      abrirMenu();
    }
  }

  return (
    <div
      ref={rootRef}
      className="barra-escrita vidro"
      data-slot="barra-escrita"
      data-modo={modo}
      data-lente={lente}
      aria-label={copy.a11y.write_bar}
      onKeyDown={(e) => {
        tecladoBarra(e);
        teclaCampo(e);
      }}
    >
      <div className="barra-escrita__linha">
        <button
          type="button"
          className="botao-icone campo-escrita__mais"
          aria-label={copy.bar.menu_hint}
          aria-haspopup="menu"
          aria-expanded={menuAberto}
          onClick={() => (menuAberto ? setMenuAberto(false) : abrirMenu())}
        >
          +
        </button>

        <div className="barra-escrita__campos" id={`${baseId}-campos`}>
          {modo === "procurar" && (
            <Procurar
              valor={texto}
              onChange={setTexto}
              onEnviar={() => void enviar()}
              inputRef={inputRef}
            />
          )}
          {modo === "correlacionar" && (
            <Correlacionar
              conceitoA={conceitoA}
              conceitoB={conceitoB}
              onChangeA={setConceitoA}
              onChangeB={setConceitoB}
              onEnviar={() => void enviar()}
            />
          )}
          {modo === "confrontar" && (
            <Confrontar
              trechoA={trechoA}
              trechoB={trechoB}
              aEscolher={aEscolher}
              onChangeA={setTrechoA}
              onChangeB={setTrechoB}
              onEscolher={setAEscolher}
              onEnviar={() => void enviar()}
            />
          )}
          {modo === "alerta" && (
            <Alerta
              valor={texto}
              onChange={setTexto}
              onEnviar={() => void enviar()}
              erroLimite={erroAlerta}
            />
          )}
          {modo === "lacunas" && (
            <Lacunas
              valor={lacunasTexto}
              onChange={setLacunasTexto}
              onEnviar={() => void enviar()}
            />
          )}
        </div>

        <PastilhaModo modo={modo} />
        <PastilhaLente lente={lente} onMudar={setLente} />

        <button
          type="button"
          className="botao-primario"
          aria-label={copy.bar.send}
          onClick={() => void enviar()}
        >
          {copy.bar.send}
        </button>
      </div>

      <MenuMais
        aberto={menuAberto}
        activo={indiceMenu}
        onSeleccionar={seleccionarModo}
      />

      {limiar !== null && (
        <p className="barra-limiar" data-testid="limiar-visivel">
          {copy.chat.threshold}: {limiar}
        </p>
      )}

      {modo === "confrontar" && aEscolher && (
        <p className="barra-dica" role="status">
          {copy.confront.pick_dim}
        </p>
      )}

      {/* Stub: citação no resultado Confrontar → leitor (PLN-15). */}
      {onAbrirCitacao ? (
        <span className="sr-only" data-abrir-citacao="stub" />
      ) : null}
    </div>
  );
}
