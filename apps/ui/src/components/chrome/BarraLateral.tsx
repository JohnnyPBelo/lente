import { useEffect, useId, useState } from "react";
import {
  apagarConversa,
  criarConversa,
  listarAlertas,
  listarConversas,
  pedirCopiaSeguranca,
  renomearConversa,
  semearConversas,
} from "../../lib/api";
import { copy } from "../../lib/copy";
import { EstadoAprendizagem } from "../aprendizagem/EstadoAprendizagem";
import { GrupoAlertas, type AlertaLista } from "../alertas/GrupoAlertas";
import { CopiaSeguranca } from "../backup/CopiaSeguranca";

export type ConversaLista = { id: string; nome: string };

export type BarraLateralProps = {
  conversas?: ConversaLista[];
  conversaActivaId?: string | null;
  onSeleccionar?: (id: string) => void;
};

type Item = { id: string; nome: string };

function paraItens(lista: ConversaLista[]): Item[] {
  return lista.map((c) => ({ id: c.id, nome: c.nome }));
}

export function BarraLateral({
  conversas,
  conversaActivaId = null,
  onSeleccionar,
}: BarraLateralProps) {
  const baseId = useId();
  const [itens, setItens] = useState<Item[]>(() =>
    conversas ? paraItens(conversas) : [],
  );
  const [activaId, setActivaId] = useState<string | null>(conversaActivaId);
  const [menuAbertoId, setMenuAbertoId] = useState<string | null>(null);
  const [aRenomearId, setARenomearId] = useState<string | null>(null);
  const [nomeRascunho, setNomeRascunho] = useState("");
  const [alertas, setAlertas] = useState<AlertaLista[]>([]);

  useEffect(() => {
    if (conversas) {
      semearConversas(
        conversas.map((c) => ({
          id: c.id,
          titulo: c.nome || null,
        })),
      );
      setItens(paraItens(conversas));
      return;
    }
    let vivo = true;
    listarConversas()
      .then((lista) => {
        if (!vivo) return;
        setItens(
          lista.map((c) => ({
            id: c.id,
            nome: c.titulo?.trim() || copy.chat.empty_title,
          })),
        );
      })
      .catch(() => {
        /* motor indisponível — lista vazia */
      });
    listarAlertas()
      .then((lista) => {
        if (!vivo) return;
        setAlertas(lista);
      })
      .catch(() => {
        /* motor indisponível */
      });
    return () => {
      vivo = false;
    };
  }, [conversas]);

  useEffect(() => {
    setActivaId(conversaActivaId);
  }, [conversaActivaId]);

  async function aoCriar() {
    const criada = await criarConversa(null);
    const nome = criada.titulo?.trim() || copy.chat.empty_title;
    setItens((prev) => [{ id: criada.id, nome }, ...prev]);
    setActivaId(criada.id);
    onSeleccionar?.(criada.id);
    setMenuAbertoId(null);
  }

  function abrirRenomear(item: Item) {
    setARenomearId(item.id);
    setNomeRascunho(item.nome);
    setMenuAbertoId(null);
  }

  async function confirmarRenomear() {
    if (!aRenomearId) {
      return;
    }
    const titulo = nomeRascunho.trim() || copy.chat.empty_title;
    await renomearConversa(aRenomearId, titulo);
    setItens((prev) =>
      prev.map((item) =>
        item.id === aRenomearId ? { ...item, nome: titulo } : item,
      ),
    );
    setARenomearId(null);
  }

  async function aoApagar(id: string) {
    await apagarConversa(id);
    setItens((prev) => prev.filter((item) => item.id !== id));
    if (activaId === id) {
      setActivaId(null);
    }
    setMenuAbertoId(null);
  }

  function seleccionar(id: string) {
    setActivaId(id);
    onSeleccionar?.(id);
    setMenuAbertoId(null);
  }

  return (
    <nav className="barra-lateral vidro" aria-label={copy.a11y.sidebar}>
      <EstadoAprendizagem />
      <CopiaSeguranca
        onCopiar={async (destino) => {
          await pedirCopiaSeguranca(destino);
        }}
      />

      <div className="barra-lateral__conversas">
        <div className="barra-lateral__cabecalho">
          <p className="barra-lateral__grupo">{copy.conversations.group}</p>
          <button
            type="button"
            className="botao-primario"
            onClick={() => void aoCriar()}
          >
            {copy.chrome.new_chat}
          </button>
        </div>

        <ul
          className="barra-lateral__lista"
          role="list"
          aria-label={copy.conversations.group}
        >
          {itens.map((item) => {
            const activo = item.id === activaId;
            const aRenomear = item.id === aRenomearId;
            return (
              <li
                key={item.id}
                className={
                  activo
                    ? "barra-lateral__item vidro-activo"
                    : "barra-lateral__item"
                }
              >
                {aRenomear ? (
                  <form
                    className="barra-lateral__renomear"
                    onSubmit={(evento) => {
                      evento.preventDefault();
                      void confirmarRenomear();
                    }}
                  >
                    <label className="sr-only" htmlFor={`${baseId}-renomear`}>
                      {copy.chrome.rename}
                    </label>
                    <input
                      id={`${baseId}-renomear`}
                      role="textbox"
                      aria-label={copy.chrome.rename}
                      value={nomeRascunho}
                      onChange={(evento) => setNomeRascunho(evento.target.value)}
                      autoFocus
                    />
                    <button type="submit" className="botao-primario">
                      {copy.chrome.confirm}
                    </button>
                    <button
                      type="button"
                      className="botao-fantasma"
                      onClick={() => setARenomearId(null)}
                    >
                      {copy.chrome.cancel}
                    </button>
                  </form>
                ) : (
                  <>
                    <button
                      type="button"
                      className="barra-lateral__nome"
                      onClick={() => seleccionar(item.id)}
                    >
                      {item.nome}
                    </button>
                    <div className="barra-lateral__menu-wrap">
                      <button
                        type="button"
                        className="botao-icone"
                        aria-label={`Mais acções da conversa ${item.nome}`}
                        title={`Mais acções da conversa ${item.nome}`}

                        aria-expanded={menuAbertoId === item.id}
                        aria-haspopup="menu"
                        onClick={() =>
                          setMenuAbertoId((actual) =>
                            actual === item.id ? null : item.id,
                          )
                        }
                      >
                        ···
                      </button>
                      {menuAbertoId === item.id ? (
                        <div className="barra-lateral__menu vidro" role="menu">
                          <button
                            type="button"
                            role="menuitem"
                            onClick={() => abrirRenomear(item)}
                          >
                            {copy.chrome.rename}
                          </button>
                          <button
                            type="button"
                            role="menuitem"
                            onClick={() => void aoApagar(item.id)}
                          >
                            {copy.chrome.delete}
                          </button>
                        </div>
                      ) : null}
                    </div>
                  </>
                )}
              </li>
            );
          })}
        </ul>
      </div>

      <GrupoAlertas
        alertas={alertas}
        alertaActivoId={activaId}
        onSeleccionar={(id) => {
          const alvo = alertas.find((a) => a.id === id);
          if (alvo?.chat_id) {
            seleccionar(alvo.chat_id);
          }
        }}
      />
    </nav>
  );
}
