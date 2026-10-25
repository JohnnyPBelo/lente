"""Validação do JSON de correções alinhada a ``docs/dados/correcoes.schema.json``."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[2]
CAMINHO_ESQUEMA = RAIZ / "docs" / "dados" / "correcoes.schema.json"

CHAVE_FORMATO = "format_version"
CHAVE_MODELO = "base_model_id"
CHAVE_CORRECOES = "corrections"
FORMATO_VERSAO = "1"

_DATA_HORA = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)

_ETIQUETAS = frozenset({"positivo", "negativo"})
_LENTES = frozenset({"investigar", "assessment", "acreditacao", "verificar"})


class CorrecoesInvalidas(ValueError):
    """JSON estruturalmente inválido ou com chaves fora do esquema."""


def carregar_esquema() -> dict[str, Any]:
    """Lê o JSON Schema canónico das correções."""
    return json.loads(CAMINHO_ESQUEMA.read_text(encoding="utf-8"))


def _tipo_ok(valor: object, tipo: str) -> bool:
    if tipo == "object":
        return isinstance(valor, dict)
    if tipo == "array":
        return isinstance(valor, list)
    if tipo == "string":
        return isinstance(valor, str)
    if tipo == "integer":
        return isinstance(valor, int) and not isinstance(valor, bool)
    if tipo == "number":
        return isinstance(valor, (int, float)) and not isinstance(valor, bool)
    if tipo == "boolean":
        return isinstance(valor, bool)
    if tipo == "null":
        return valor is None
    raise CorrecoesInvalidas(f"Tipo de esquema não suportado: {tipo}.")


def _validar_instancia(valor: object, esquema: dict[str, Any], caminho: str) -> None:
    """Subconjunto do verificador de ``docs/desenvolvimento/regressao.md``."""
    if "const" in esquema and valor != esquema["const"]:
        raise CorrecoesInvalidas(f"{caminho} devia ser {esquema['const']!r}.")
    if "enum" in esquema and valor not in esquema["enum"]:
        raise CorrecoesInvalidas(f"{caminho} não está no enum {esquema['enum']!r}.")
    tipos = esquema.get("type")
    if isinstance(tipos, str):
        tipos = [tipos]
    if tipos and not any(_tipo_ok(valor, tipo) for tipo in tipos):
        raise CorrecoesInvalidas(f"{caminho} não cumpre o tipo {tipos!r}.")
    if isinstance(valor, str):
        if "minLength" in esquema and len(valor) < esquema["minLength"]:
            raise CorrecoesInvalidas(f"{caminho} é mais curto do que minLength.")
        if esquema.get("format") == "date-time" and _DATA_HORA.fullmatch(valor) is None:
            raise CorrecoesInvalidas(f"{caminho} não é uma data-hora ISO-8601 aceite.")
    if isinstance(valor, dict):
        for chave in esquema.get("required", []):
            if chave not in valor:
                raise CorrecoesInvalidas(
                    f"{caminho} não tem a chave obrigatória {chave}."
                )
        propriedades = esquema.get("properties", {})
        extra = esquema.get("additionalProperties", True)
        for chave, filho in valor.items():
            if chave in propriedades:
                _validar_instancia(filho, propriedades[chave], f"{caminho}.{chave}")
            elif extra is False:
                raise CorrecoesInvalidas(
                    f"{caminho} tem a chave não prevista {chave}."
                )
            elif isinstance(extra, dict):
                _validar_instancia(filho, extra, f"{caminho}.{chave}")
    if isinstance(valor, list):
        item = esquema.get("items")
        if isinstance(item, dict):
            for indice, filho in enumerate(valor):
                _validar_instancia(filho, item, f"{caminho}[{indice}]")


def validar_pacote(dados: object) -> dict[str, Any]:
    """Valida e devolve o pacote; levanta ``CorrecoesInvalidas`` se falhar.

    O único artefacto aceite para juntar afinações é o JSON de correções
    (REQ-FOR-003): binários LoRA e chaves de pesos são recusados.
    """
    if isinstance(dados, (bytes, bytearray)):
        raise CorrecoesInvalidas(
            "Só se aceita JSON de correções; binários LoRA estão fora de âmbito."
        )
    if not isinstance(dados, dict):
        raise CorrecoesInvalidas("O artefacto de correções tem de ser um objecto JSON.")
    try:
        _validar_instancia(dados, carregar_esquema(), "$")
    except CorrecoesInvalidas:
        raise
    # Garantias explícitas alinhadas ao enum do esquema.
    for i, correcao in enumerate(dados.get(CHAVE_CORRECOES, [])):
        if correcao.get("etiqueta") not in _ETIQUETAS:
            raise CorrecoesInvalidas(f"$.corrections[{i}].etiqueta inválida.")
        if correcao.get("lente") not in _LENTES:
            raise CorrecoesInvalidas(f"$.corrections[{i}].lente inválida.")
    return dados
