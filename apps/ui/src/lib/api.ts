/** Cliente HTTP local. Em testes e sem motor: respostas falsas em memória. */

export type LentePedido =
  | "investigar"
  | "assessment"
  | "acreditacao"
  | "verificar";

export const BASE_URL = "http://127.0.0.1:4317";

export type ConversaResumo = {
  id: string;
  titulo: string | null;
  actualizado_em?: string;
};

export type MensagemFalsa =
  | { id: string; papel: "utilizador"; texto: string }
  | {
      id: string;
      papel: "assistente";
      frases?: string[];
      texto?: string;
      excertos?: { n: number; documento_id: string; pagina: number }[];
    };

type ChatInterno = {
  id: string;
  titulo: string | null;
  mensagens: MensagemFalsa[];
  actualizado_em: string;
};

let sequencia = 0;
let chats: ChatInterno[] = [];
let usarFalso = true;
let limiarActual = 0.55;
let alertasFalsos: { id: string; texto: string; lente: LentePedido }[] = [];

function agoraIso(): string {
  return new Date().toISOString();
}

function novoId(prefixo: string): string {
  sequencia += 1;
  return `${prefixo}_${String(sequencia).padStart(2, "0")}`;
}

export function reiniciarApiFalsa(): void {
  sequencia = 0;
  chats = [];
  usarFalso = true;
  limiarActual = 0.55;
  alertasFalsos = [];
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
  const resposta = await fetch(`${BASE_URL}${caminho}`, {
    ...init,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
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

export async function procurar(pedido: {
  chat_id: string;
  texto: string;
  lente: LentePedido;
}): Promise<{ ok: true; lente: LentePedido }> {
  if (!usarFalso) {
    await pedir<unknown>("/search", {
      method: "POST",
      body: JSON.stringify(pedido),
    });
  }
  return { ok: true, lente: pedido.lente };
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
