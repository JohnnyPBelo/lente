"""Motor de procura por omissão: excertos sem E2B (doubles / degradação)."""

from __future__ import annotations

from typing import Any


def motor_procura_sem_e2b(
    *,
    chat_id: str,
    texto: str,
    lente: str,
    pagina_aberta: dict[str, Any] | None = None,
    com_e2b: bool = False,
    **_kwargs: Any,
) -> dict[str, Any]:
    """Sem índice/recuperação ligada: devolve vazio (a API emite evento ``vazio``).

    Os testes injectam um double com fixture indexada. Quando PLN-07/11
    estiverem disponíveis no processo, o entrypoint (PLN-21) substitui este
    motor por um que chama ``engine.pesquisa`` + ``engine.resposta``.
    """
    del chat_id, texto, lente, pagina_aberta, com_e2b
    return {"excertos": [], "frases": [], "miniaturas": []}
