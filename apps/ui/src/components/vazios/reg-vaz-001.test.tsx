import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { copy } from "../../lib/copy";
import { BibliotecaVazia } from "./BibliotecaVazia";
import { ConversaNova } from "./ConversaNova";
import { ModeloADescarregar } from "./ModeloADescarregar";
import { PaginaSemTexto } from "./PaginaSemTexto";
import { ProcuraSemDocumentos } from "./ProcuraSemDocumentos";
import { ProsaFiltrada } from "./ProsaFiltrada";
import { UrlRecusada } from "./UrlRecusada";

describe("REG-VAZ-001", () => {
  it("biblioteca sem ficheiros usa copy canónica", () => {
    render(<BibliotecaVazia />);
    expect(screen.getByText(copy.vazios.biblioteca.titulo)).toBeInTheDocument();
    expect(screen.getByText(copy.vazios.biblioteca.corpo)).toBeInTheDocument();
  });

  it("modelo a descarregar indica o caminho", () => {
    const caminho = "models/gemma-4-e2b-qat-q4";
    render(<ModeloADescarregar caminho={caminho} />);
    expect(screen.getByText(copy.vazios.modelo.titulo)).toBeInTheDocument();
    expect(screen.getByText(new RegExp(caminho))).toBeInTheDocument();
  });

  it("prosa filtrada sem prosa fantasma", () => {
    render(<ProsaFiltrada excertos={["Trecho real."]} />);
    expect(screen.getByText(copy.vazios.prosa.titulo)).toBeInTheDocument();
    expect(screen.getByText(copy.vazios.prosa.corpo)).toBeInTheDocument();
    expect(screen.getByText("Trecho real.")).toBeInTheDocument();
    expect(screen.getByTestId("prosa-fantasma")).not.toBeVisible();
  });

  it("página sem texto", () => {
    render(<PaginaSemTexto />);
    expect(screen.getByText(copy.vazios.pagina.titulo)).toBeInTheDocument();
    expect(screen.getByText(copy.vazios.pagina.corpo)).toBeInTheDocument();
  });

  it("URL recusada", () => {
    render(<UrlRecusada />);
    expect(screen.getByText(copy.vazios.url.titulo)).toBeInTheDocument();
    expect(screen.getByText(copy.vazios.url.corpo)).toBeInTheDocument();
  });

  it("conversa nova", () => {
    render(<ConversaNova />);
    expect(screen.getByText(copy.vazios.conversa.titulo)).toBeInTheDocument();
    expect(screen.getByText(copy.vazios.conversa.corpo)).toBeInTheDocument();
  });

  it("procura sem documentos sem miniaturas falsas", () => {
    render(<ProcuraSemDocumentos />);
    expect(screen.getByText(copy.vazios.procura.titulo)).toBeInTheDocument();
    expect(screen.getByText(copy.vazios.procura.corpo)).toBeInTheDocument();
    expect(screen.getByTestId("miniaturas-falsas")).not.toBeVisible();
    expect(screen.queryByRole("img")).toBeNull();
  });
});
