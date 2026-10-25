"""Prefixos EmbeddingGemma 2 para documentos e queries (por lente)."""

from __future__ import annotations

# Lentes → task (docs/modelos/prefixos-e-lentes.md).
_TASK_QUESTION = frozenset({"investigar", "acreditacao"})
_TASK_FACT = frozenset({"verificar", "assessment"})


def prefixo_documento(titulo: str | None, conteudo: str) -> str:
    """Forma a entrada de indexação: ``title: … | text: …``."""
    rotulo = titulo.strip() if titulo and titulo.strip() else "none"
    return f"title: {rotulo} | text: {conteudo}"


def prefixo_query(consulta: str, *, lente: str | None = None) -> str:
    """Forma a query conforme a lente activa (ou procura curta em repouso)."""
    chave = (lente or "").strip().casefold()
    if chave in _TASK_QUESTION:
        tarefa = "question answering"
    elif chave in _TASK_FACT:
        tarefa = "fact checking"
    else:
        tarefa = "search result"
    return f"task: {tarefa} | query: {consulta}"


__all__ = ["prefixo_documento", "prefixo_query"]
