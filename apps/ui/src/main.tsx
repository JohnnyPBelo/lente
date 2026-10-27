import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { Onboarding } from "./components/onboarding/Onboarding";
import "./styles/global.css";

const raiz = document.getElementById("raiz");
if (!raiz) {
  throw new Error("Elemento #raiz em falta");
}

createRoot(raiz).render(
  <StrictMode>
    <App />
    <Onboarding />
  </StrictMode>,
);
