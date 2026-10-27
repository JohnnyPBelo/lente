/**
 * Introdução dismissível no primeiro uso.
 * Monta-se fora de App.tsx para evitar conflitos de rebase no chrome.
 */

import { useCallback, useEffect, useId, useState } from "react";
import { duracaoMotionMs, prefersReducedMotion } from "../../a11y/focos";
import { baseUrl } from "../../lib/api";
import { copy } from "../../lib/copy";
import {
  deveMostrarOnboarding,
  gravarJaVi,
  IDS_PASSOS_ONBOARDING,
  type IdPassoOnboarding,
} from "../../lib/onboarding";

export type EstadoModeloUi = "pronto" | "ausente";

export type OnboardingProps = {
  /** Força visibilidade (testes). */
  aberto?: boolean;
  /** Storage injectável (testes). */
  armazenamento?: Storage;
  /** Query string injectável (testes). */
  pesquisa?: string;
  /** Estado dos modelos injectável (testes). */
  estadosModelos?: Partial<Record<"embedding" | "juiz" | "escritor", EstadoModeloUi>>;
  onDismiss?: () => void;
};

type EstadosModelos = Record<"embedding" | "juiz" | "escritor", EstadoModeloUi>;

function estadoDeApi(valor: unknown): EstadoModeloUi {
  if (
    valor &&
    typeof valor === "object" &&
    "estado" in valor &&
    (valor as { estado: string }).estado === "pronto"
  ) {
    return "pronto";
  }
  return "ausente";
}

export function Onboarding({
  aberto: abertoForcado,
  armazenamento,
  pesquisa,
  estadosModelos: estadosInjectados,
  onDismiss,
}: OnboardingProps) {
  const tituloId = useId();
  const [visivel, setVisivel] = useState(() =>
    abertoForcado ??
      deveMostrarOnboarding({ armazenamento, pesquisa }),
  );
  const [indice, setIndice] = useState(0);
  const [modelos, setModelos] = useState<EstadosModelos>(() => ({
    embedding: estadosInjectados?.embedding ?? "ausente",
    juiz: estadosInjectados?.juiz ?? "ausente",
    escritor: estadosInjectados?.escritor ?? "ausente",
  }));

  const reduzir = prefersReducedMotion();
  const duracao = duracaoMotionMs(reduzir);

  useEffect(() => {
    if (abertoForcado != null) {
      setVisivel(abertoForcado);
    }
  }, [abertoForcado]);

  useEffect(() => {
    if (estadosInjectados) {
      setModelos({
        embedding: estadosInjectados.embedding ?? "ausente",
        juiz: estadosInjectados.juiz ?? "ausente",
        escritor: estadosInjectados.escritor ?? "ausente",
      });
      return;
    }
    if (!visivel) return;
    let vivo = true;
    (async () => {
      try {
        const res = await fetch(`${baseUrl()}/models/status`);
        if (!res.ok || !vivo) return;
        const corpo = (await res.json()) as Record<string, unknown>;
        if (!vivo) return;
        setModelos({
          embedding: estadoDeApi(corpo.embedding),
          juiz: estadoDeApi(corpo.juiz),
          escritor: estadoDeApi(corpo.escritor),
        });
      } catch {
        /* motor a subir — o passo modelos fica genérico */
      }
    })();
    return () => {
      vivo = false;
    };
  }, [estadosInjectados, visivel]);

  const dispensar = useCallback(() => {
    gravarJaVi(armazenamento);
    setVisivel(false);
    onDismiss?.();
  }, [armazenamento, onDismiss]);

  useEffect(() => {
    if (!visivel) return;
    function aoTecla(ev: KeyboardEvent) {
      if (ev.key === "Escape") {
        ev.preventDefault();
        dispensar();
      }
    }
    window.addEventListener("keydown", aoTecla);
    return () => window.removeEventListener("keydown", aoTecla);
  }, [dispensar, visivel]);

  if (!visivel) return null;

  const idPasso = IDS_PASSOS_ONBOARDING[indice]!;
  const passo = copy.onboarding.passos[idPasso];
  const total = IDS_PASSOS_ONBOARDING.length;
  const rotuloPasso = copy.onboarding.passo_de
    .replace("{actual}", String(indice + 1))
    .replace("{total}", String(total));

  return (
    <div
      className="onboarding-fundo"
      data-reduced-motion={reduzir ? "reduce" : "no-preference"}
      style={{ ["--lente-motion-ms" as string]: `${duracao}ms` }}
    >
      <div
        className="onboarding vidro"
        role="dialog"
        aria-modal="true"
        aria-labelledby={tituloId}
        data-testid="onboarding"
        data-passo={idPasso}
      >
        <header className="onboarding__cabecalho">
          <h2 id={tituloId}>{copy.onboarding.title}</h2>
          <p className="onboarding__passo" role="status">
            {rotuloPasso}
          </p>
        </header>

        <PassoConteudo id={idPasso} passo={passo} modelos={modelos} />

        <footer className="onboarding__acoes">
          <button
            type="button"
            className="botao-fantasma"
            disabled={indice === 0}
            onClick={() => setIndice((i) => Math.max(0, i - 1))}
          >
            {copy.onboarding.anterior}
          </button>
          {indice < total - 1 ? (
            <button
              type="button"
              className="botao-primario"
              onClick={() => setIndice((i) => Math.min(total - 1, i + 1))}
            >
              {copy.onboarding.seguinte}
            </button>
          ) : null}
          <button
            type="button"
            className="botao-primario"
            data-testid="onboarding-ja-vi"
            onClick={dispensar}
          >
            {copy.onboarding.ja_vi}
          </button>
        </footer>
      </div>
    </div>
  );
}

function PassoConteudo({
  id,
  passo,
  modelos,
}: {
  id: IdPassoOnboarding;
  passo: { titulo: string; corpo: string };
  modelos: EstadosModelos;
}) {
  return (
    <section
      className="onboarding__corpo estado-vazio"
      data-estado={`onboarding-${id}`}
      aria-labelledby={`onboarding-passo-${id}`}
    >
      <h3 id={`onboarding-passo-${id}`}>{passo.titulo}</h3>
      <p>{passo.corpo}</p>
      {id === "modelos" ? (
        <ul className="onboarding__modelos" data-testid="onboarding-modelos">
          {(
            [
              ["embedding", copy.onboarding.passos.modelos.embedding],
              ["juiz", copy.onboarding.passos.modelos.juiz],
              ["escritor", copy.onboarding.passos.modelos.escritor],
            ] as const
          ).map(([chave, rotulo]) => (
            <li key={chave} data-estado={modelos[chave]}>
              <span>{rotulo}</span>
              <span>
                {modelos[chave] === "pronto"
                  ? copy.onboarding.passos.modelos.pronto
                  : copy.onboarding.passos.modelos.ausente}
              </span>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
