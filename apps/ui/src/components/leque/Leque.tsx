import { useEffect, useState } from "react";
import { copy } from "../../lib/copy";
import { Miniatura, type MiniaturaDoc } from "./Miniatura";

export type LequeProps = {
  documentos: MiniaturaDoc[];
  onAbrir: (documentoId: string) => void;
  /** tacto: primeiro toque abre leque */
  tacto?: boolean;
};

function reducedMotion(): boolean {
  if (typeof window === "undefined" || !window.matchMedia) {
    return false;
  }
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function Leque({ documentos, onAbrir, tacto = false }: LequeProps) {
  const [aberto, setAberto] = useState(documentos.length <= 1);
  const [toque, setToque] = useState(0);
  const curto = reducedMotion();

  useEffect(() => {
    if (documentos.length <= 1) {
      setAberto(true);
    }
  }, [documentos.length]);

  if (documentos.length === 0) {
    return null;
  }

  if (documentos.length === 1) {
    const unico = documentos[0]!;
    return (
      <div
        className="leque leque--unico"
        data-reduced-motion={curto ? "true" : "false"}
        data-animacao={curto ? "curta" : "nominal"}
        aria-label={copy.a11y.fan}
      >
        <Miniatura doc={unico} onAbrir={onAbrir} />
      </div>
    );
  }

  function aoTocarConjunto() {
    if (!tacto) return;
    if (toque === 0) {
      setAberto(true);
      setToque(1);
    }
  }

  return (
    <div
      className={aberto ? "leque leque--aberto" : "leque"}
      data-reduced-motion={curto ? "true" : "false"}
      data-animacao={curto ? "curta" : "nominal"}
      data-aberto={aberto ? "true" : "false"}
      aria-label={copy.a11y.fan}
      onTouchStart={aoTocarConjunto}
      onMouseEnter={() => {
        if (!tacto) setAberto(true);
      }}
      onFocusCapture={() => {
        if (!tacto) setAberto(true);
      }}
    >
      <ul className="leque__lista" role="list">
        {documentos.map((doc) => (
          <li key={doc.documento_id} role="listitem">
            <Miniatura
              doc={doc}
              onFoco={() => setAberto(true)}
              onAbrir={(id) => {
                if (tacto && toque < 1) {
                  setAberto(true);
                  setToque(1);
                  return;
                }
                onAbrir(id);
              }}
            />
          </li>
        ))}
      </ul>
    </div>
  );
}
