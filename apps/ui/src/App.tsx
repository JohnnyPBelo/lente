import { useCallback, useEffect, useRef, useState } from "react";
import { AreaChat } from "./components/chrome/AreaChat";
import { BarraLateral } from "./components/chrome/BarraLateral";
import { BarraEscrita, type ResultadoBarra } from "./components/barra/BarraEscrita";
import { PainelBiblioteca } from "./components/biblioteca/PainelBiblioteca";
import { MensagemComDocumentos } from "./components/chat/MensagemComDocumentos";
import { SlotLeitor } from "./components/leitor/SlotLeitor";
import { ProcuraSemDocumentos } from "./components/vazios/ProcuraSemDocumentos";
import { BotaoFecharDossier } from "./components/dossier/BotaoFecharDossier";
import {
  criarConversa,
  fecharDossier,
  listarConversas,
  obterConversa,
  type MensagemFalsa,
  type MiniaturaMsg,
} from "./lib/api";
import { copy } from "./lib/copy";
import type { MiniaturaDoc } from "./components/leque/Miniatura";

/**
 * Composição do chrome: conversa → biblioteca → procura → excertos/leque.
 * Modos da barra (correlate/confront/alerta/lacunas) renderizam no fio.
 */
export function App() {
  const [conversaActivaId, setConversaActivaId] = useState<string | null>(null);
  const [mensagens, setMensagens] = useState<MensagemFalsa[]>([]);
  const [vistaBiblioteca, setVistaBiblioteca] = useState(false);
  const [miniaturasActivas, setMiniaturasActivas] = useState<MiniaturaDoc[]>([]);
  const [mensagemLeitorId, setMensagemLeitorId] = useState<string | undefined>();
  const [listaEpoch, setListaEpoch] = useState(0);
  const [avisoModo, setAvisoModo] = useState<string | null>(null);
  const criarConversaEmCurso = useRef<Promise<string> | null>(null);

  const aplicarAssistente = useCallback((ultima: MensagemFalsa | undefined) => {
    if (!ultima || ultima.papel !== "assistente") {
      setMiniaturasActivas([]);
      setMensagemLeitorId(undefined);
      return;
    }
    const mini = (ultima.miniaturas ?? []).map(
      (m: MiniaturaMsg): MiniaturaDoc => ({
        documento_id: m.documento_id,
        pagina: m.pagina,
        url: m.url ?? "",
      }),
    );
    setMiniaturasActivas(mini);
    setMensagemLeitorId(ultima.id);
  }, []);

  const carregarConversa = useCallback(
    async (id: string) => {
      const detalhe = await obterConversa(id);
      setMensagens(detalhe.mensagens);
      setConversaActivaId(id);
      const ultima = [...detalhe.mensagens]
        .reverse()
        .find((m) => m.papel === "assistente");
      aplicarAssistente(ultima);
    },
    [aplicarAssistente],
  );

  useEffect(() => {
    let vivo = true;
    (async () => {
      try {
        const lista = await listarConversas();
        if (!vivo) return;
        if (lista.length > 0) {
          await carregarConversa(lista[0]!.id);
        }
      } catch {
        /* motor ainda a subir */
      }
    })();
    return () => {
      vivo = false;
    };
  }, [carregarConversa]);

  const aoSeleccionar = useCallback(
    (id: string) => {
      setVistaBiblioteca(false);
      setAvisoModo(null);
      void carregarConversa(id);
    },
    [carregarConversa],
  );

  const garantirConversa = useCallback(async (): Promise<string> => {
    if (conversaActivaId) return conversaActivaId;
    if (!criarConversaEmCurso.current) {
      criarConversaEmCurso.current = criarConversa(null)
        .then((criada) => {
          setConversaActivaId(criada.id);
          setMensagens([]);
          setListaEpoch((n) => n + 1);
          return criada.id;
        })
        .finally(() => {
          criarConversaEmCurso.current = null;
        });
    }
    return criarConversaEmCurso.current;
  }, [conversaActivaId]);

  const aoResultado = useCallback(
    async (r: ResultadoBarra) => {
      setAvisoModo(null);

      if (r.tipo === "alerta") {
        setAvisoModo(
          r.ok
            ? "Alerta criado — aparece no grupo Alertas da barra lateral."
            : r.erro || copy.alerts.limit,
        );
        setListaEpoch((n) => n + 1);
        return;
      }

      if (r.tipo === "confrontar") {
        const assistente: MensagemFalsa = {
          id: r.resposta.mensagem_id ?? `msg_local_a_${Date.now()}`,
          papel: "assistente",
          texto: `${leituraConfrontar(r.resposta.leitura)} (${r.resposta.score.toFixed(2)})`,
          frases: [
            r.resposta.trecho_a.texto,
            r.resposta.trecho_b.texto,
          ].filter(Boolean),
        };
        setMensagens((prev) => [
          ...prev,
          {
            id: `msg_local_${Date.now()}`,
            papel: "utilizador",
            texto: "Confrontar",
          },
          assistente,
        ]);
        return;
      }

      if (r.tipo === "correlacionar") {
        const eventos = r.resposta.eventos ?? [];
        const excertos = eventos
          .filter((e) => e.documento_id)
          .map((e, i) => ({
            n: i + 1,
            documento_id: e.documento_id,
            pagina: e.pagina,
            texto: e.texto,
          }));
        const assistente: MensagemFalsa = {
          id: r.resposta.mensagem_id ?? `msg_local_a_${Date.now()}`,
          papel: "assistente",
          excertos,
          texto:
            excertos.length === 0
              ? "Sem documentos no índice para estes conceitos."
              : excertos.map((e) => e.texto).filter(Boolean).join("\n"),
          frases: excertos.map((e) => e.texto || "").filter(Boolean),
        };
        setMensagens((prev) => [
          ...prev,
          {
            id: `msg_local_${Date.now()}`,
            papel: "utilizador",
            texto: `${r.conceito_a} ↔ ${r.conceito_b}`,
          },
          assistente,
        ]);
        aplicarAssistente(assistente);
        return;
      }

      if (r.tipo === "lacunas") {
        const linhas = (r.resposta.itens ?? []).map(
          (i) => `${i.estado}: ${i.linha}`,
        );
        const assistente: MensagemFalsa = {
          id: r.resposta.mensagem_id ?? `msg_local_a_${Date.now()}`,
          papel: "assistente",
          texto: linhas.join("\n") || "Sem linhas.",
          frases: linhas,
        };
        setMensagens((prev) => [
          ...prev,
          {
            id: `msg_local_${Date.now()}`,
            papel: "utilizador",
            texto: "Lacunas",
          },
          assistente,
        ]);
        return;
      }

      if (r.tipo !== "procurar") return;
      // Usa o chat_id da procura (já criada na barra) — evita segundo POST /chats.
      const chatId = r.chat_id;
      setConversaActivaId(chatId);
      setListaEpoch((n) => n + 1);
      try {
        await carregarConversa(chatId);
        if (!r.resposta.vazio) {
          const mini = r.resposta.miniaturas.map(
            (m): MiniaturaDoc => ({
              documento_id: m.documento_id,
              pagina: m.pagina,
              url: m.url ?? "",
            }),
          );
          setMiniaturasActivas(mini);
          setMensagemLeitorId(r.resposta.mensagem_id);
        }
      } catch {
        const idUser = `msg_local_${Date.now()}`;
        const assistente: MensagemFalsa = {
          id: r.resposta.mensagem_id ?? `msg_local_a_${Date.now()}`,
          papel: "assistente",
          frases: r.resposta.frases,
          excertos: r.resposta.excertos,
          miniaturas: r.resposta.miniaturas,
          texto: r.resposta.excertos
            .map((e) => e.texto)
            .filter(Boolean)
            .join("\n"),
        };
        setMensagens((prev) => [
          ...prev,
          { id: idUser, papel: "utilizador", texto: r.texto },
          assistente,
        ]);
        aplicarAssistente(assistente);
      }
    },
    [aplicarAssistente, carregarConversa],
  );

  return (
    <div className="app-chrome">
      <BarraLateral
        key={listaEpoch}
        conversaActivaId={conversaActivaId}
        onSeleccionar={aoSeleccionar}
      />
      <main className="app-principal">
        <div className="app-principal__topo" data-slot="barra-modos">
          <button
            type="button"
            className="botao-fantasma"
            aria-pressed={vistaBiblioteca}
            onClick={() => setVistaBiblioteca((v) => !v)}
          >
            {copy.lib.title}
          </button>
          {conversaActivaId ? (
            <BotaoFecharDossier
              onFechar={async () => {
                await fecharDossier(conversaActivaId);
                setAvisoModo("Dossier fechado.");
              }}
            />
          ) : null}
        </div>

        {avisoModo ? (
          <p role="status" className="aviso-modo">
            {avisoModo}
          </p>
        ) : null}

        {vistaBiblioteca ? (
          <PainelBiblioteca onFechar={() => setVistaBiblioteca(false)} />
        ) : (
          <>
            <AreaChat
              mensagens={mensagens}
              renderAssistente={(mensagem) => {
                if (mensagem.papel !== "assistente") return null;
                const excertos = mensagem.excertos ?? [];
                const miniaturas = (mensagem.miniaturas ?? []).map(
                  (m): MiniaturaDoc => ({
                    documento_id: m.documento_id,
                    pagina: m.pagina,
                    url: m.url ?? "",
                  }),
                );
                const frasesFonte =
                  mensagem.frases && mensagem.frases.length
                    ? mensagem.frases.map((texto, i) => ({
                        texto,
                        n: i + 1,
                        destino: {
                          n: excertos[0]?.n ?? i + 1,
                          documento_id: excertos[0]?.documento_id ?? "",
                          pagina: excertos[0]?.pagina ?? 1,
                        },
                      }))
                    : excertos
                        .filter((e) => e.texto)
                        .map((e) => ({
                          texto: e.texto!,
                          n: e.n,
                          destino: {
                            n: e.n,
                            documento_id: e.documento_id,
                            pagina: e.pagina,
                          },
                        }));
                if (
                  !frasesFonte.length &&
                  !miniaturas.length &&
                  !excertos.length &&
                  !mensagem.texto
                ) {
                  return <ProcuraSemDocumentos />;
                }
                if (!frasesFonte.length && mensagem.texto) {
                  return (
                    <div className="mensagem-docs">
                      <p className="mensagem-assistente__texto">{mensagem.texto}</p>
                    </div>
                  );
                }
                return (
                  <MensagemComDocumentos
                    mensagemId={mensagem.id}
                    miniaturas={miniaturas}
                    frases={frasesFonte}
                    onAbrirDoc={(id) => {
                      setMiniaturasActivas((prev) =>
                        prev.some((m) => m.documento_id === id)
                          ? prev
                          : [
                              ...prev,
                              { documento_id: id, pagina: 1, url: "" },
                            ],
                      );
                    }}
                    onAbrirCitacao={(d) => {
                      setMiniaturasActivas((prev) =>
                        prev.some((m) => m.documento_id === d.documento_id)
                          ? prev
                          : [
                              ...prev,
                              {
                                documento_id: d.documento_id,
                                pagina: d.pagina,
                                url: "",
                              },
                            ],
                      );
                    }}
                  />
                );
              }}
            />
            <BarraEscrita
              chatId={conversaActivaId}
              onGarantirChat={garantirConversa}
              onResultado={(r) => {
                void aoResultado(r);
              }}
            />
            <SlotLeitor
              mensagemId={mensagemLeitorId}
              chatId={conversaActivaId ?? undefined}
              miniaturas={miniaturasActivas}
            />
          </>
        )}
      </main>
    </div>
  );
}

function leituraConfrontar(leitura: string): string {
  if (leitura === "concordam") return copy.confront.reading_agree;
  if (leitura === "contradizem-se") return copy.confront.reading_contradict;
  return copy.confront.reading_different;
}
