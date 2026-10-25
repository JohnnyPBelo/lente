import { BarraLateral } from "./components/chrome/BarraLateral";

/**
 * Composição do chrome. Sítios nomeados e vazios para PLN-14 (barra de modos)
 * e PLN-15 (leitor) — sem os implementar aqui.
 */
export function App() {
  return (
    <div className="app-chrome">
      <BarraLateral />
      <main className="app-principal">
        <div data-slot="barra-modos" aria-hidden="true" />
        <div data-slot="area-chat" />
        <div data-slot="barra-escrita" />
        <div data-slot="leitor" aria-hidden="true" />
      </main>
    </div>
  );
}
