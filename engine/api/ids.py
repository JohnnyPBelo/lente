"""IDs opacos do contrato HTTP (cht_…, doc_…, msg_…)."""

from __future__ import annotations


class IdInvalido(ValueError):
    """Prefixo ou forma de identificador inválida."""


def formatar(prefixo: str, numero: int) -> str:
    return f"{prefixo}_{numero}"


def analisar(valor: str, prefixo: str) -> int:
    esperado = f"{prefixo}_"
    if not isinstance(valor, str) or not valor.startswith(esperado):
        raise IdInvalido(f"Identificador inválido: {valor!r}")
    resto = valor[len(esperado) :]
    if not resto.isdigit():
        raise IdInvalido(f"Identificador inválido: {valor!r}")
    return int(resto)


def chat_id(numero: int) -> str:
    return formatar("cht", numero)


def doc_id(numero: int) -> str:
    return formatar("doc", numero)


def msg_id(numero: int) -> str:
    return formatar("msg", numero)


def dos_id(numero: int) -> str:
    return formatar("dos", numero)


def analisar_chat(valor: str) -> int:
    return analisar(valor, "cht")


def analisar_doc(valor: str) -> int:
    return analisar(valor, "doc")


def analisar_dos(valor: str) -> int:
    return analisar(valor, "dos")


def analisar_msg(valor: str) -> int:
    return analisar(valor, "msg")
