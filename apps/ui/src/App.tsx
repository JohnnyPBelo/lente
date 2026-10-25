import { useCallback, useState } from "react";
import { AreaChat } from "./components/chrome/AreaChat";
import { BarraLateral } from "./components/chrome/BarraLateral";
import { CampoEscritaBase } from "./components/chrome/CampoEscritaBase";
import type { MensagemFalsa } from "./lib/api";

/**
 * Composição do chrome. Sítios nomeados e vazios para PLN-14 (barra de modos)
 * e PLN-15 (leitor) — sem os implementar aqui.
 */
export function App() {
  const [conversaActivaId, setConversaActivaId] = useState<string | null>(null);
  const [mensagens, setMensagens] = useState<MensagemFalsa[]>([]);

  const aoSeleccionar = useCallback((id: string) => {
    setConversaActivaId(id);
    setMensagens([]);
  }, []);

  const aoEnviar = useCallback((texto: string) => {
    const id = `msg_local_${Date.now()}`;
    setMensagens((prev) => [...prev, { id, papel: "utilizador", texto }]);
  }, []);

  return (
    <div className="app-chrome">
      <BarraLateral
        conversaActivaId={conversaActivaId}
        onSeleccionar={aoSeleccionar}
      />
      <main className="app-principal">
        {/* PLN-14: barra de modos e lentes */}
        <div data-slot="barra-modos" className="slot-vazio" />
        <AreaChat mensagens={mensagens} />
        <CampoEscritaBase onEnviar={aoEnviar} />
        {/* PLN-15: leque e leitor */}
        <div data-slot="leitor" className="slot-vazio" aria-hidden="true" />
      </main>
    </div>
  );
}
