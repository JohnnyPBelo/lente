/** Cliente HTTP local. Em testes: respostas falsas; em build/runtime: motor real. */

export type LentePedido =
  | "investigar"
  | "assessment"
  | "acreditacao"
  | "verificar";

/** Origem do motor que serve a UI (mesmo porto que o browser). */
export function baseUrl(): string {
  if (typeof window !== "undefined" && window.location?.origin) {
    const origem = window.location.origin;
    if (origem && origem !== "null" && !origem.startsWith("file:")) {
      return origem;
    }
  }
  return "http://127.0.0.1:4317";
}

/** @deprecated Preferir ``baseUrl()`` — qualquer porto do ``engine.cli``. */
export const BASE_URL = "http://127.0.0.1:4317";

export type ConversaResumo = {
  id: string;
  titulo: string | null;
  actualizado_em?: string;
};

export type ExcertoMsg = {
  n: number;
  documento_id: string;
  pagina: number;
  texto?: string;
};

export type MiniaturaMsg = {
  documento_id: string;
  pagina: number;
  url?: string;
};

export type MensagemFalsa =
  | { id: string; papel: "utilizador"; texto: string }
  | {
      id: string;
      papel: "assistente";
      frases?: string[];
      texto?: string;
      excertos?: ExcertoMsg[];
      miniaturas?: MiniaturaMsg[];
    };

type ChatInterno = {
  id: string;
  titulo: string | null;
  mensagens: MensagemFalsa[];
  actualizado_em: string;
};

let sequencia = 0;
let chats: ChatInterno[] = [];
/** Em Vitest ``reiniciarApiFalsa`` activa o falso; no build fica o motor real. */
let usarFalso = false;
let limiarActual = 0.55;
let alertasFalsos: { id: string; texto: string; lente: LentePedido }[] = [];

function agoraIso(): string {
  return new Date().toISOString();
}

function novoId(prefixo: string): string {
  sequencia += 1;
  return `${prefixo}_${String(sequencia).padStart(2, "0")}`;
}

export type DocumentoLeitor = {
  id: string;
  titulo: string;
  tipo: "pdf" | "texto" | "markdown" | "url" | "imagem";
  paginas: number;
  hash_sha256: string;
  desactualizado: boolean;
  sumario: { titulo: string; pagina: number }[];
  etiquetas: string[];
};

export type PaginaLeitor = {
  pagina: number;
  texto: string;
  largura: number;
  altura: number;
};

export type HighlightApi = {
  n: number;
  pagina: number;
  offsets: { inicio: number; fim: number };
  caixas?: { pagina: number; x: number; y: number; w: number; h: number }[];
  mensagem_id?: string;
};

let documentosFalsos: Record<string, DocumentoLeitor> = {};
let paginasFalsas: Record<string, PaginaLeitor> = {};
let highlightsFalsos: Record<string, HighlightApi[]> = {};
let fixadosFalsos: {
  id: string;
  chat_id: string;
  documento_id: string;
  pagina: number;
  texto: string;
  offsets: { inicio: number; fim: number };
}[] = [];

export function reiniciarApiFalsa(): void {
  sequencia = 0;
  chats = [];
  usarFalso = true;
  limiarActual = 0.55;
  alertasFalsos = [];
  documentosFalsos = {};
  paginasFalsas = {};
  highlightsFalsos = {};
  fixadosFalsos = [];
}

export function activarApiFalsa(activo = true): void {
  usarFalso = activo;
}

async function pedir<T>(
  caminho: string,
  init?: RequestInit,
): Promise<T | null> {
  if (usarFalso) {
    return null;
  }
  const cabecalhos: Record<string, string> = {
    Accept: "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };
  if (init?.body != null && !(init.body instanceof FormData)) {
    cabecalhos["Content-Type"] =
      cabecalhos["Content-Type"] ?? "application/json";
  }
  const resposta = await fetch(`${baseUrl()}${caminho}`, {
    ...init,
    headers: cabecalhos,
  });
  if (resposta.status === 204) {
    return null;
  }
  if (!resposta.ok) {
    throw new Error(`HTTP ${resposta.status} em ${caminho}`);
  }
  return (await resposta.json()) as T;
}

export async function listarConversas(): Promise<ConversaResumo[]> {
  const remoto = await pedir<{ itens: ConversaResumo[] }>("/chats");
  if (remoto) {
    return remoto.itens;
  }
  return chats.map((c) => ({
    id: c.id,
    titulo: c.titulo,
    actualizado_em: c.actualizado_em,
  }));
}

export async function criarConversa(
  titulo: string | null = null,
): Promise<ConversaResumo & { mensagens: MensagemFalsa[] }> {
  const corpo = JSON.stringify({ titulo });
  const remoto = await pedir<{
    id: string;
    titulo: string | null;
    mensagens: MensagemFalsa[];
  }>("/chats", { method: "POST", body: corpo });
  if (remoto) {
    return remoto;
  }
  const criado: ChatInterno = {
    id: novoId("cht"),
    titulo,
    mensagens: [],
    actualizado_em: agoraIso(),
  };
  chats = [criado, ...chats];
  return {
    id: criado.id,
    titulo: criado.titulo,
    mensagens: criado.mensagens,
  };
}

export async function renomearConversa(
  id: string,
  titulo: string,
): Promise<ConversaResumo> {
  const remoto = await pedir<ConversaResumo>(`/chats/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ titulo }),
  });
  if (remoto) {
    return remoto;
  }
  const alvo = chats.find((c) => c.id === id);
  if (!alvo) {
    throw new Error(`Conversa ${id} não encontrada`);
  }
  alvo.titulo = titulo;
  alvo.actualizado_em = agoraIso();
  return { id: alvo.id, titulo: alvo.titulo, actualizado_em: alvo.actualizado_em };
}

export async function apagarConversa(id: string): Promise<void> {
  if (!usarFalso) {
    await pedir<null>(`/chats/${id}`, { method: "DELETE" });
    return;
  }
  chats = chats.filter((c) => c.id !== id);
}

export async function obterConversa(id: string): Promise<{
  id: string;
  titulo: string | null;
  mensagens: MensagemFalsa[];
}> {
  const remoto = await pedir<{
    id: string;
    titulo: string | null;
    mensagens: MensagemFalsa[];
  }>(`/chats/${id}`);
  if (remoto) {
    return remoto;
  }
  const alvo = chats.find((c) => c.id === id);
  if (!alvo) {
    throw new Error(`Conversa ${id} não encontrada`);
  }
  return {
    id: alvo.id,
    titulo: alvo.titulo,
    mensagens: alvo.mensagens,
  };
}

/** Semente a memória falsa (só testes / demo). */
export function semearConversas(
  itens: { id: string; titulo: string | null }[],
): void {
  chats = itens.map((item) => ({
    id: item.id,
    titulo: item.titulo,
    mensagens: [],
    actualizado_em: agoraIso(),
  }));
}


/* ——— Modos da barra (PLN-14) ——— */

export async function obterLimiar(): Promise<number> {
  return limiarActual;
}

export function definirLimiarFalso(valor: number): void {
  limiarActual = valor;
}

export type ResultadoProcura = {
  ok: true;
  lente: LentePedido;
  mensagem_id?: string;
  excertos: ExcertoMsg[];
  miniaturas: MiniaturaMsg[];
  frases: string[];
  vazio: boolean;
};

function parseSse(corpo: string): Record<string, unknown>[] {
  const eventos: Record<string, unknown>[] = [];
  for (const bloco of corpo.split("\n\n")) {
    const linha = bloco
      .split("\n")
      .map((l) => l.trim())
      .find((l) => l.startsWith("data:"));
    if (!linha) continue;
    try {
      eventos.push(JSON.parse(linha.slice(5).trim()) as Record<string, unknown>);
    } catch {
      /* ignore */
    }
  }
  return eventos;
}

export async function procurar(pedido: {
  chat_id: string;
  texto: string;
  lente: LentePedido;
}): Promise<ResultadoProcura> {
  if (usarFalso) {
    return {
      ok: true,
      lente: pedido.lente,
      excertos: [],
      miniaturas: [],
      frases: [],
      vazio: true,
    };
  }
  const resposta = await fetch(`${baseUrl()}/search`, {
    method: "POST",
    headers: {
      Accept: "text/event-stream",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(pedido),
  });
  if (!resposta.ok) {
    throw new Error(`HTTP ${resposta.status} em /search`);
  }
  const eventos = parseSse(await resposta.text());
  const excertos: ExcertoMsg[] = [];
  const miniaturas: MiniaturaMsg[] = [];
  const frases: string[] = [];
  let mensagemId: string | undefined;
  let vazio = false;
  for (const ev of eventos) {
    const tipo = ev.tipo;
    if (tipo === "excerto") {
      excertos.push({
        n: Number(ev.n ?? excertos.length + 1),
        documento_id: String(ev.documento_id ?? ""),
        pagina: Number(ev.pagina ?? 1),
        texto: typeof ev.texto === "string" ? ev.texto : undefined,
      });
    } else if (tipo === "miniaturas" && Array.isArray(ev.itens)) {
      for (const item of ev.itens as MiniaturaMsg[]) {
        miniaturas.push(item);
      }
    } else if (tipo === "frase") {
      if (typeof ev.texto === "string") frases.push(ev.texto);
    } else if (tipo === "vazio") {
      vazio = true;
    } else if (tipo === "fim" && typeof ev.mensagem_id === "string") {
      mensagemId = ev.mensagem_id;
    }
  }
  if (!excertos.length && !frases.length) {
    vazio = true;
  }
  return {
    ok: true,
    lente: pedido.lente,
    mensagem_id: mensagemId,
    excertos,
    miniaturas,
    frases,
    vazio,
  };
}

export async function listarBiblioteca(): Promise<
  {
    id: string;
    titulo: string;
    etiquetas: string[];
    desactualizado: boolean;
    tipo_sugerido: string | null;
  }[]
> {
  const remoto = await pedir<{
    itens: {
      id: string;
      titulo: string;
      etiquetas: string[];
      desactualizado: boolean;
      tipo_sugerido: string | null;
    }[];
  }>("/library");
  return remoto?.itens ?? [];
}

export async function ingerirFicheiro(
  ficheiro: File,
): Promise<{ documento_id: string; estado: string }> {
  if (usarFalso) {
    return { documento_id: "doc_falso", estado: "ok" };
  }
  const corpo = new FormData();
  corpo.append("ficheiros", ficheiro, ficheiro.name);
  const resposta = await fetch(`${baseUrl()}/library/ingest`, {
    method: "POST",
    headers: { Accept: "application/json" },
    body: corpo,
  });
  if (!resposta.ok) {
    throw new Error(`HTTP ${resposta.status} em /library/ingest`);
  }
  return (await resposta.json()) as { documento_id: string; estado: string };
}

export async function correlacionar(pedido: {
  chat_id: string;
  conceito_a: string;
  conceito_b: string;
  lente: LentePedido;
}): Promise<{
  mensagem_id: string;
  papeis: string[];
  eventos: {
    papel: string;
    texto: string;
    documento_id: string;
    pagina: number;
  }[];
  conceito_a: string;
  conceito_b: string;
  lente: LentePedido;
}> {
  if (!usarFalso) {
    const remoto = await pedir<Record<string, unknown>>("/correlate", {
      method: "POST",
      body: JSON.stringify(pedido),
    });
    if (remoto) {
      return remoto as never;
    }
  }
  return {
    mensagem_id: novoId("msg"),
    papeis: ["A", "B", "relacao"],
    conceito_a: pedido.conceito_a,
    conceito_b: pedido.conceito_b,
    lente: pedido.lente,
    eventos: [
      {
        papel: "A",
        texto: pedido.conceito_a,
        documento_id: "doc_a",
        pagina: 1,
      },
      {
        papel: "B",
        texto: pedido.conceito_b,
        documento_id: "doc_b",
        pagina: 1,
      },
      {
        papel: "relacao",
        texto: `${pedido.conceito_a} ↔ ${pedido.conceito_b}`,
        documento_id: "doc_rel",
        pagina: 1,
      },
    ],
  };
}

export async function confrontar(pedido: {
  chat_id: string;
  trecho_a: {
    texto: string;
    documento_id?: string;
    pagina?: number;
  };
  trecho_b: {
    texto: string;
    documento_id?: string;
    pagina?: number;
  };
  _cos?: number;
  _j_ab?: number;
  _j_ba?: number;
}): Promise<{
  mensagem_id: string;
  leitura: "concordam" | "contradizem-se" | "assuntos_diferentes";
  score: number;
  trecho_a: { documento_id?: string; pagina?: number; texto: string };
  trecho_b: { documento_id?: string; pagina?: number; texto: string };
}> {
  if (!usarFalso) {
    const remoto = await pedir<Record<string, unknown>>("/confront", {
      method: "POST",
      body: JSON.stringify(pedido),
    });
    if (remoto) {
      return remoto as never;
    }
  }
  const cos = pedido._cos ?? 0.12;
  const jAb = pedido._j_ab ?? 0.08;
  const jBa = pedido._j_ba ?? 0.07;
  let leitura: "concordam" | "contradizem-se" | "assuntos_diferentes" =
    "assuntos_diferentes";
  if (cos < 0.35) {
    leitura = "assuntos_diferentes";
  } else if (Math.min(jAb, jBa) >= 0.55) {
    leitura = "concordam";
  } else if (
    cos >= 0.5 &&
    Math.max(jAb, jBa) >= 0.55 &&
    Math.abs(jAb - jBa) >= 0.3
  ) {
    leitura = "contradizem-se";
  } else if (cos >= 0.5 && Math.min(jAb, jBa) < 0.4) {
    leitura = "contradizem-se";
  }
  return {
    mensagem_id: novoId("msg"),
    leitura,
    score: (jAb + jBa) / 2,
    trecho_a: {
      documento_id: pedido.trecho_a.documento_id,
      pagina: pedido.trecho_a.pagina,
      texto: pedido.trecho_a.texto,
    },
    trecho_b: {
      documento_id: pedido.trecho_b.documento_id,
      pagina: pedido.trecho_b.pagina,
      texto: pedido.trecho_b.texto,
    },
  };
}

export async function lacunas(pedido: {
  chat_id: string;
  linhas: string[];
  lente: LentePedido;
}): Promise<{
  mensagem_id: string;
  itens: { linha: string; estado: "encontrado" | "fraco" | "ausente" }[];
  escritor_chamado: false;
  lente: LentePedido;
}> {
  if (!usarFalso) {
    const remoto = await pedir<Record<string, unknown>>("/lacunas", {
      method: "POST",
      body: JSON.stringify(pedido),
    });
    if (remoto) {
      return remoto as never;
    }
  }
  return {
    mensagem_id: novoId("msg"),
    lente: pedido.lente,
    escritor_chamado: false,
    itens: pedido.linhas.map((linha) => ({
      linha,
      estado: "ausente" as const,
    })),
  };
}

export async function criarAlerta(pedido: {
  texto: string;
  lente: LentePedido;
}): Promise<
  | { id: string; chat_id: string; activo: true }
  | { erro: "limite_alertas"; mensagem: string }
> {
  if (!usarFalso) {
    try {
      const remoto = await pedir<{ id: string; chat_id: string; activo: true }>(
        "/alerts",
        { method: "POST", body: JSON.stringify(pedido) },
      );
      if (remoto) {
        return remoto;
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : "";
      if (msg.includes("409")) {
        return {
          erro: "limite_alertas",
          mensagem: "Máximo de dez alertas.",
        };
      }
      throw e;
    }
  }
  if (alertasFalsos.length >= 10) {
    return { erro: "limite_alertas", mensagem: "Máximo de dez alertas." };
  }
  const id = novoId("ale");
  alertasFalsos.push({ id, texto: pedido.texto, lente: pedido.lente });
  return { id, chat_id: novoId("cht_al"), activo: true };
}

export function semearAlertasFalsos(n: number): void {
  alertasFalsos = Array.from({ length: n }, (_, i) => ({
    id: `ale_${i + 1}`,
    texto: `alerta ${i + 1}`,
    lente: "investigar" as LentePedido,
  }));
}

export function listarAlertasFalsos(): typeof alertasFalsos {
  return [...alertasFalsos];
}


export function semearDocumento(
  doc: DocumentoLeitor,
  paginas: PaginaLeitor[] = [],
  highlights: HighlightApi[] = [],
): void {
  documentosFalsos[doc.id] = doc;
  for (const p of paginas) {
    paginasFalsas[`${doc.id}:${p.pagina}`] = p;
  }
  highlightsFalsos[doc.id] = highlights;
}

export async function obterDocumento(id: string): Promise<DocumentoLeitor> {
  if (!usarFalso) {
    const r = await pedir<DocumentoLeitor>(`/documents/${id}`);
    if (r) return r;
  }
  return (
    documentosFalsos[id] ?? {
      id,
      titulo: id,
      tipo: "texto",
      paginas: 1,
      hash_sha256: "a".repeat(64),
      desactualizado: false,
      sumario: [],
      etiquetas: [],
    }
  );
}

export async function obterPagina(
  documentoId: string,
  pagina: number,
): Promise<PaginaLeitor> {
  if (!usarFalso) {
    const r = await pedir<PaginaLeitor>(
      `/documents/${documentoId}/pages/${pagina}`,
    );
    if (r) return r;
  }
  return (
    paginasFalsas[`${documentoId}:${pagina}`] ?? {
      pagina,
      texto: "",
      largura: 595,
      altura: 842,
    }
  );
}

export async function obterHighlights(
  documentoId: string,
  mensagemId?: string,
): Promise<HighlightApi[]> {
  if (!usarFalso) {
    const q = mensagemId ? `?mensagem_id=${encodeURIComponent(mensagemId)}` : "";
    const r = await pedir<{ itens: HighlightApi[] }>(
      `/documents/${documentoId}/highlights${q}`,
    );
    if (r) return r.itens;
  }
  const todos = highlightsFalsos[documentoId] ?? [];
  if (!mensagemId) return todos;
  return todos.filter((h) => !h.mensagem_id || h.mensagem_id === mensagemId);
}

export async function fixarTrecho(
  chatId: string,
  trecho: {
    documento_id: string;
    pagina: number;
    texto: string;
    offsets: { inicio: number; fim: number };
  },
): Promise<{ id: string }> {
  if (!usarFalso) {
    const r = await pedir<{ id: string }>(`/chats/${chatId}/fixados`, {
      method: "POST",
      body: JSON.stringify(trecho),
    });
    if (r) return r;
  }
  const id = novoId("fix");
  fixadosFalsos.push({ id, chat_id: chatId, ...trecho });
  return { id };
}

export function listarFixadosFalsos(chatId: string) {
  return fixadosFalsos.filter((f) => f.chat_id === chatId);
}
