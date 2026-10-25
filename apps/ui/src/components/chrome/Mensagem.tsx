import { useEffect, useState, type ReactNode } from "react";

export type MensagemProps = {
  papel: "utilizador" | "assistente";
  children: ReactNode;
};

function reduzMotion(): boolean {
  if (typeof window === "undefined" || !window.matchMedia) {
    return false;
  }
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function Mensagem({ papel, children }: MensagemProps) {
  const [visível, setVisível] = useState(() => reduzMotion());

  useEffect(() => {
    if (reduzMotion()) {
      setVisível(true);
      return;
    }
    const id = requestAnimationFrame(() => setVisível(true));
    return () => cancelAnimationFrame(id);
  }, []);

  return (
    <article
      className={
        visível
          ? `mensagem mensagem--${papel} mensagem--entrada`
          : `mensagem mensagem--${papel}`
      }
      data-papel={papel}
    >
      <div className="mensagem__corpo">{children}</div>
    </article>
  );
}
