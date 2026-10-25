"""Resolver caminhos em ``models/`` e mensagens se os pesos faltarem."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from engine.embeddings.carregar import caminho_pesos as caminho_embedding
from engine.juiz.caminhos import caminho_onnx, pasta_juiz
from engine.resposta.e2b import caminho_gguf, pasta_e2b

EstadoModelo = Literal["pronto", "a_descarregar", "em_falta", "erro_licenca"]

Papel = Literal["embedding", "juiz", "escritor"]

# Caminhos canónicos alinhados a docs/desenvolvimento/ambiente.md e ao contrato.
CAMINHO_EMBEDDING = "models/embeddinggemma-2"
CAMINHO_JUIZ = "models/juiz"
CAMINHO_ESCRITOR = "models/e2b"


def caminhos_esperados(raiz_modelos: Path | str | None = None) -> dict[Papel, str]:
    """Caminhos relativos (ou sob ``raiz_modelos``) onde pôr cada peso."""
    if raiz_modelos is None:
        return {
            "embedding": CAMINHO_EMBEDDING,
            "juiz": CAMINHO_JUIZ,
            "escritor": CAMINHO_ESCRITOR,
        }
    raiz = Path(raiz_modelos)
    return {
        "embedding": str(caminho_embedding(raiz)),
        "juiz": str(pasta_juiz(raiz)),
        "escritor": str(pasta_e2b(raiz)),
    }


def _pasta_tem_conteudo(pasta: Path) -> bool:
    return pasta.is_dir() and any(pasta.iterdir())


def _estado_papel(
    papel: Papel,
    raiz: Path,
    *,
    forcar: dict[Papel, EstadoModelo] | None = None,
) -> EstadoModelo:
    if forcar and papel in forcar:
        return forcar[papel]
    if papel == "embedding":
        return "pronto" if _pasta_tem_conteudo(caminho_embedding(raiz)) else "em_falta"
    if papel == "juiz":
        onnx = caminho_onnx(raiz)
        return "pronto" if onnx.is_file() or _pasta_tem_conteudo(pasta_juiz(raiz)) else "em_falta"
    gguf = caminho_gguf(raiz)
    return "pronto" if gguf.is_file() else "em_falta"


def estado_modelos(
    raiz_modelos: Path | str | None = None,
    *,
    forcar: dict[Papel, EstadoModelo] | None = None,
) -> dict[str, Any]:
    """Estado HTTP-models-status (sem descarregar pesos)."""
    raiz = Path(raiz_modelos) if raiz_modelos is not None else Path("models")
    caminhos = caminhos_esperados(raiz)
    resultado: dict[str, Any] = {}
    for papel in ("embedding", "juiz", "escritor"):
        estado = _estado_papel(papel, raiz, forcar=forcar)  # type: ignore[arg-type]
        if estado == "pronto":
            resultado[papel] = {"estado": "pronto", "caminho": caminhos[papel]}  # type: ignore[index]
        else:
            entrada: dict[str, Any] = {
                "estado": estado,
                "caminho_esperado": caminhos[papel],  # type: ignore[index]
            }
            if papel == "escritor":
                entrada["tamanho_aprox_gb"] = 3
            resultado[papel] = entrada
    return resultado


def _mensagem_orientacao(papel: Papel, caminho: str) -> str:
    if papel == "embedding":
        return (
            f"Coloca o EmbeddingGemma 2 (só texto) em {caminho}. "
            "Sem estes pesos a procura semântica fica limitada."
        )
    if papel == "juiz":
        return (
            f"Coloca o juiz ONNX int8 em {caminho}. "
            "Sem o juiz não há highlights acima do limiar."
        )
    return (
        f"Coloca os pesos Q4 em {caminho}. "
        "Sem o E2B o chat segue com excertos e miniaturas."
    )


def orientar_falta(
    raiz_modelos: Path | str | None = None,
    *,
    forcar: dict[Papel, EstadoModelo] | None = None,
) -> dict[str, Any]:
    """Orientação HTTP-models-guidance para pesos em falta ou licença bloqueada."""
    estado = estado_modelos(raiz_modelos, forcar=forcar)
    itens: list[dict[str, Any]] = []
    for papel, info in estado.items():
        if info.get("estado") in {"em_falta", "erro_licenca", "a_descarregar"}:
            caminho = str(info.get("caminho_esperado") or info.get("caminho") or "")
            itens.append(
                {
                    "modelo": papel,
                    "mensagem": _mensagem_orientacao(papel, caminho),  # type: ignore[arg-type]
                    "url_documentacao": None,
                    "caminho": caminho,
                }
            )
    return {"itens": itens}


def estados_health(
    raiz_modelos: Path | str | None = None,
    *,
    forcar: dict[Papel, EstadoModelo] | None = None,
) -> dict[str, str]:
    """Mapa compacto para ``GET /health`` → ``modelos``."""
    estado = estado_modelos(raiz_modelos, forcar=forcar)
    saida: dict[str, str] = {}
    for papel, info in estado.items():
        raw = str(info.get("estado", "ausente"))
        if raw == "pronto":
            saida[papel] = "pronto"
        else:
            # Contrato /health usa «ausente» quando não está pronto.
            saida[papel] = "ausente"
    return saida
