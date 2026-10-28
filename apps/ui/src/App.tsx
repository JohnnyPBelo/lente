import { useCallback, useEffect, useRef, useState } from "react";
import { AreaChat } from "./components/chrome/AreaChat";
import { BarraLateral } from "./components/chrome/BarraLateral";
import { BarraEscrita, type ResultadoBarra } from "./components/barra/BarraEscrita";
import { PainelBiblioteca } from "./components/biblioteca/PainelBiblioteca";
import { MensagemComDocumentos } from "./components/chat/MensagemComDocumentos";
import { SlotLeitor } from "./components/leitor/SlotLeitor";
import { ProcuraSemDocumentos } from "./components/vazios/ProcuraSemDocumentos";
import { BotaoFecharDossier } from "./components/dossier/BotaoFecharDossier";
import type { DestinoLeitor } from "./components/leque/LequeLeitor";
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
  const [destinoLeitor, setDestinoLeitor] = useState<DestinoLeitor | null>(null);
  const [listaEpoch, setListaEpoch] = useState(0);
  const [avisoModo, setAvisoModo] = useState<string | null>(null);
  const criarConversaEmCurso = useRef<Promise<string> | null>(null);

  const aplicarAssistente = useCallback((ultima: MensagemFalsa | undefined) => {
    if (!ultima || ultima.papel !== "assistente") {
      setMiniaturasActivas([]);
      setMensagemLeitorId(undefined);
      setDestinoLeitor(null);
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
    setDestinoLeitor(null);
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

  const garantirMiniatura = useCallback((documentoId: string, pagina = 1) => {
    setMiniaturasActivas((prev) =>
      prev.some((m) => m.documento_id === documentoId)
        ? prev
        : [...prev, { documento_id: documentoId, pagina, url: "" }],
    );
  }, []);

  const aoAbrirCitacao = useCallback(
    (d: { documento_id: string; pagina: number; n: number }) => {
      if (!d.documento_id) return;
      garantirMiniatura(d.documento_id, d.pagina);
      setDestinoLeitor({
        documento_id: d.documento_id,
        pagina: d.pagina,
        n: d.n,
      });
    },
    [garantirMiniatura],
  );

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
        const cos = Number(r.resposta.cos ?? 0);
        const jAb = Number(r.resposta.j_ab ?? 0);
        const jBa = Number(r.resposta.j_ba ?? 0);
        const assistente: MensagemFalsa = {
          id: r.resposta.mensagem_id ?? `msg_local_a_${Date.now()}`,
          papel: "assistente",
          texto: `${leituraConfrontar(r.resposta.leitura)} (${r.resposta.score.toFixed(2)}; cos ${cos.toFixed(2)}; j_ab ${jAb.toFixed(2)}; j_ba ${jBa.toFixed(2)})`,
          frases: [
            r.resposta.trecho_a.texto,
            r.resposta.trecho_b.texto,
          ].filter(Boolean),
          confronto: {
            leitura: r.resposta.leitura,
            score: r.resposta.score,
            cos,
            j_ab: jAb,
            j_ba: jBa,
          },
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
        const excertosCorrelacao = eventos
          .filter((e) => e.documento_id && e.texto)
          .map((e, i) => ({
            n: i + 1,
            papel: (e.papel === "B" || e.papel === "relacao"
              ? e.papel
              : "A") as "A" | "B" | "relacao",
            documento_id: e.documento_id,
            pagina: e.pagina ?? 1,
            texto: e.texto,
          }));
        const miniaturas = dedupeMiniaturas(
          excertosCorrelacao.map((e) => ({
            documento_id: e.documento_id,
            pagina: e.pagina,
            url: "",
          })),
        );
        const assistente: MensagemFalsa = {
          id: r.resposta.mensagem_id ?? `msg_local_a_${Date.now()}`,
          papel: "assistente",
          correlacionar: true,
          excertosCorrelacao,
          excertos: excertosCorrelacao.map((e) => ({
            n: e.n,
            documento_id: e.documento_id,
            pagina: e.pagina,
            texto: e.texto,
          })),
          miniaturas,
          texto:
            excertosCorrelacao.length === 0
              ? "Sem documentos no índice para estes conceitos."
              : undefined,
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
        const itens = (r.resposta.itens ?? []).map((i) => ({
          linha: i.linha,
          estado: i.estado,
          citacao: i.citacao ?? null,
        }));
        const assistente: MensagemFalsa = {
          id: r.resposta.mensagem_id ?? `msg_local_a_${Date.now()}`,
          papel: "assistente",
          lacunas: itens,
          texto: itens.map((i) => `${i.estado}: ${i.linha}`).join("\n") || "Sem linhas.",
          excertos: itens
            .filter((i) => i.citacao?.documento_id)
            .map((i, idx) => ({
              n: idx + 1,
              documento_id: i.citacao!.documento_id,
              pagina: i.citacao!.pagina,
              texto: i.citacao?.texto,
            })),
          miniaturas: dedupeMiniaturas(
            itens
              .filter((i) => i.citacao?.documento_id)
              .map((i) => ({
                documento_id: i.citacao!.documento_id,
                pagina: i.citacao!.pagina,
                url: "",
              })),
          ),
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
        aplicarAssistente(assistente);
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
          setDestinoLeitor(null);
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

                if (mensagem.correlacionar) {
                  const excertos = mensagem.excertosCorrelacao ?? [];
                  const miniaturas = (mensagem.miniaturas ?? []).map(
                    (m): MiniaturaDoc => ({
                      documento_id: m.documento_id,
                      pagina: m.pagina,
                      url: m.url ?? "",
                    }),
                  );
                  if (!excertos.length && !mensagem.texto) {
                    return <ProcuraSemDocumentos />;
                  }
                  return (
                    <div className="mensagem-docs-com-leitura">
                      {mensagem.texto ? (
                        <p className="mensagem-assistente__texto" role="status">
                          {mensagem.texto}
                        </p>
                      ) : null}
                      <MensagemComDocumentos
                        mensagemId={mensagem.id}
                        correlacionar
                        excertos={excertos}
                        miniaturas={miniaturas}
                        frases={[]}
                        onAbrirDoc={(id) => garantirMiniatura(id)}
                        onAbrirCitacao={aoAbrirCitacao}
                      />
                    </div>
                  );
                }

                if (mensagem.lacunas) {
                  const frasesFonte = mensagem.lacunas.map((item, i) => {
                    const cit = item.citacao;
                    return {
                      texto: `${item.estado}: ${item.linha}`,
                      n: i + 1,
                      destino:
                        item.estado !== "ausente" && cit?.documento_id
                          ? {
                              n: i + 1,
                              documento_id: cit.documento_id,
                              pagina: cit.pagina,
                            }
                          : null,
                    };
                  });
                  const miniaturas = (mensagem.miniaturas ?? []).map(
                    (m): MiniaturaDoc => ({
                      documento_id: m.documento_id,
                      pagina: m.pagina,
                      url: m.url ?? "",
                    }),
                  );
                  return (
                    <div className="mensagem-docs-com-leitura">
                      <MensagemComDocumentos
                        mensagemId={mensagem.id}
                        miniaturas={miniaturas}
                        frases={frasesFonte}
                        onAbrirDoc={(id) => garantirMiniatura(id)}
                        onAbrirCitacao={aoAbrirCitacao}
                      />
                    </div>
                  );
                }

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
                    ? mensagem.frases.map((texto, i) => {
                        const ex = excertos[i] ?? excertos[0];
                        return {
                          texto,
                          n: i + 1,
                          destino: ex?.documento_id
                            ? {
                                n: ex.n ?? i + 1,
                                documento_id: ex.documento_id,
                                pagina: ex.pagina ?? 1,
                              }
                            : null,
                        };
                      })
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
                  <div className="mensagem-docs-com-leitura">
                    {mensagem.texto && mensagem.confronto ? (
                      <p className="mensagem-assistente__texto" role="status">
                        {mensagem.texto}
                      </p>
                    ) : mensagem.texto && !frasesFonte.length ? (
                      <p className="mensagem-assistente__texto" role="status">
                        {mensagem.texto}
                      </p>
                    ) : null}
                    <MensagemComDocumentos
                      mensagemId={mensagem.id}
                      miniaturas={miniaturas}
                      frases={frasesFonte}
                      onAbrirDoc={(id) => garantirMiniatura(id)}
                      onAbrirCitacao={aoAbrirCitacao}
                    />
                  </div>
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
              destino={destinoLeitor}
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

function dedupeMiniaturas(
  itens: { documento_id: string; pagina: number; url: string }[],
): MiniaturaMsg[] {
  const vistos = new Set<string>();
  const saida: MiniaturaMsg[] = [];
  for (const item of itens) {
    if (vistos.has(item.documento_id)) continue;
    vistos.add(item.documento_id);
    saida.push(item);
  }
  return saida;
}
