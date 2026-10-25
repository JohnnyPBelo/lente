"""Prefixos de lente aplicados à consulta do alerta (sem E2B)."""

from __future__ import annotations

# Alinhado a docs/modelos/prefixos-e-lentes.md — a lente muda o critério; sem prosa.
_PREFIXOS: dict[str | None, str] = {
    "investigar": "task: question answering | query: ",
    "acreditacao": "task: question answering | query: ",
    "verificar": "task: fact checking | query: ",
    "assessment": "task: fact checking | query: ",
    None: "task: search result | query: ",
}


def consulta_com_prefixo(consulta: str, lente: str | None) -> str:
    """Devolve a pergunta enviada ao juiz com o prefixo da lente."""
    prefixo = _PREFIXOS.get(lente, _PREFIXOS[None])
    return f"{prefixo}{consulta}"
