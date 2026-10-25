import { useCallback, useEffect, useState } from "react";
import { AreaChat } from "./components/chrome/AreaChat";
import { BarraLateral } from "./components/chrome/BarraLateral";
import { BarraEscrita, type ResultadoBarra } from "./components/barra/BarraEscrita";
import { PainelBiblioteca } from "./components/biblioteca/PainelBiblioteca";
import { MensagemComDocumentos } from "./components/chat/MensagemComDocumentos";
import { SlotLeitor } from "./components/leitor/SlotLeitor";
import { ProcuraSemDocumentos } from "./components/vazios/ProcuraSemDocumentos";
import {
  criarConversa,
  listarConversas,
  obterConversa,
  type MensagemFalsa,
  type MiniaturaMsg,
} from "./lib/api";
import { copy } from "./lib/copy";
import type { MiniaturaDoc } from "./components/leque/Miniatura";

/**
 * Composição do chrome: conversa → biblioteca → procura → excertos/leque.
 */
export function App() {
  const [conversaActivaId, setConversaActivaId] = useState<string | null>(null);
  const [mensagens, setMensagens] = useState<MensagemFalsa[]>([]);
  const [vistaBiblioteca, setVistaBiblioteca] = useState(false);
  const [miniaturasActivas, setMiniaturasActivas] = useState<MiniaturaDoc[]>([]);
  const [mensagemLeitorId, setMensagemLeitorId] = useState<string | undefined>();

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
      void carregarConversa(id);
    },
    [carregarConversa],
  );

  const garantirConversa = useCallback(async (): Promise<string> => {
    if (conversaActivaId) return conversaActivaId;
    const criada = await criarConversa(null);
    setConversaActivaId(criada.id);
    setMensagens([]);
    return criada.id;
  }, [conversaActivaId]);

  const aoResultado = useCallback(
    async (r: ResultadoBarra) => {
      if (r.tipo !== "procurar") return;
      const chatId = await garantirConversa();
      // O motor já gravou o turno; recarrega o fio real.
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
    [aplicarAssistente, carregarConversa, garantirConversa],
  );

  return (
    <div className="app-chrome">
      <BarraLateral
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
        </div>

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
                  !excertos.length
                ) {
                  return <ProcuraSemDocumentos />;
                }
                return (
                  <MensagemComDocumentos
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
              chatId={conversaActivaId ?? "cht_01"}
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
