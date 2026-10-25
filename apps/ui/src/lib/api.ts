/** Cliente HTTP local. Em testes e sem motor: respostas falsas em memória. */

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
