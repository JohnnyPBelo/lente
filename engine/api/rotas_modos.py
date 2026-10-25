"""Rotas HTTP-correlate, HTTP-confront e HTTP-lacunas (contrato-http.md).

Sem FastAPI obrigatório: handlers puros. Quem montar a app (PLN-12) regista-os.
Confrontar é determinístico (ADR-010 / docs/modelos/confronto.md): não chama E2B
nem muda com a lente.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal, Mapping, MutableMapping, Sequence

Leitura = Literal["concordam", "contradizem-se", "assuntos_diferentes"]

TAU_TOP = 0.35
TAU_AGR = 0.55
TAU_MES = 0.50
TAU_FRACO = 0.40
DELTA = 0.30

EscritorChamado = Callable[[], None]


@dataclass(frozen=True)
class TrechoEntrada:
    texto: str
    documento_id: str | None = None
    pagina: int | None = None
    offsets: Mapping[str, int] | None = None


def leitura_confronto(*, cos: float, j_ab: float, j_ba: float) -> Leitura:
    """Regra fixa de docs/modelos/confronto.md (ordem 1–5)."""
    if cos < TAU_TOP:
        return "assuntos_diferentes"
    if min(j_ab, j_ba) >= TAU_AGR:
        return "concordam"
    if (
        cos >= TAU_MES
        and max(j_ab, j_ba) >= TAU_AGR
        and abs(j_ab - j_ba) >= DELTA
    ):
        return "contradizem-se"
    if cos >= TAU_MES and min(j_ab, j_ba) < TAU_FRACO:
        return "contradizem-se"
    return "assuntos_diferentes"


def _trecho_de(d: Mapping[str, Any] | None) -> TrechoEntrada:
    if not d:
        return TrechoEntrada(texto="")
    return TrechoEntrada(
        texto=str(d.get("texto") or ""),
        documento_id=d.get("documento_id"),
        pagina=d.get("pagina"),
        offsets=d.get("offsets"),
    )


def confrontar(
    pedido: Mapping[str, Any],
    *,
    pontuar: Callable[[str, str], float] | None = None,
    cosseno: Callable[[str, str], float] | None = None,
    mensagem_id: str = "msg_confront",
) -> dict[str, Any]:
    """HTTP-confront: leitura determinística a partir das duas direcções + cosseno.

    `pontuar(a, b)` devolve j em (0,1). `cosseno(a, b)` devolve cos em [-1,1].
    Em falta, usa valores injectáveis via pedido['_cos'], ['_j_ab'], ['_j_ba']
    (só testes) ou defaults neutros.
    """
    a = _trecho_de(pedido.get("trecho_a") if isinstance(pedido.get("trecho_a"), Mapping) else None)
    b = _trecho_de(pedido.get("trecho_b") if isinstance(pedido.get("trecho_b"), Mapping) else None)
    if not a.texto.strip() or not b.texto.strip():
        return {
            "erro": "trechos_em_falta",
            "mensagem": "Trecho A e Trecho B são obrigatórios.",
        }

    if "_cos" in pedido and "_j_ab" in pedido and "_j_ba" in pedido:
        cos = float(pedido["_cos"])
        j_ab = float(pedido["_j_ab"])
        j_ba = float(pedido["_j_ba"])
    else:
        cos_fn = cosseno or (lambda _x, _y: 0.0)
        pont_fn = pontuar or (lambda _x, _y: 0.0)
        cos = float(cos_fn(a.texto, b.texto))
        j_ab = float(pont_fn(a.texto, b.texto))
        j_ba = float(pont_fn(b.texto, a.texto))

    leitura = leitura_confronto(cos=cos, j_ab=j_ab, j_ba=j_ba)
    score = round((j_ab + j_ba) / 2.0, 4)
    return {
        "mensagem_id": mensagem_id,
        "leitura": leitura,
        "score": score,
        "cos": cos,
        "j_ab": j_ab,
        "j_ba": j_ba,
        "trecho_a": {
            "documento_id": a.documento_id,
            "pagina": a.pagina,
            "texto": a.texto,
        },
        "trecho_b": {
            "documento_id": b.documento_id,
            "pagina": b.pagina,
            "texto": b.texto,
        },
    }


def correlacionar(
    pedido: Mapping[str, Any],
    *,
    mensagem_id: str = "msg_correlate",
    pesquisar: Callable[[str, str], Sequence[Mapping[str, Any]]] | None = None,
) -> dict[str, Any]:
    """HTTP-correlate: devolve excertos com papel A | B | relacao (mínimo)."""
    conceito_a = str(pedido.get("conceito_a") or "").strip()
    conceito_b = str(pedido.get("conceito_b") or "").strip()
    lente = str(pedido.get("lente") or "investigar")
    if not conceito_a or not conceito_b:
        return {
            "erro": "conceitos_em_falta",
            "mensagem": "Conceito A e Conceito B são obrigatórios.",
        }

    def _pesquisa_default(conceito: str, papel: str) -> list[dict[str, Any]]:
        return [
            {
                "tipo": "excerto",
                "n": 1 if papel == "A" else 2 if papel == "B" else 3,
                "papel": papel,
                "documento_id": f"doc_{papel.lower()}",
                "pagina": 1,
                "texto": conceito,
                "offsets": {"inicio": 0, "fim": len(conceito)},
                "caixas": [],
                "score_juiz": 0.7,
            }
        ]

    fn = pesquisar
    if fn is None:
        eventos: list[dict[str, Any]] = []
        eventos.extend(_pesquisa_default(conceito_a, "A"))
        eventos.extend(_pesquisa_default(conceito_b, "B"))
        eventos.append(
            {
                "tipo": "excerto",
                "n": 3,
                "papel": "relacao",
                "documento_id": "doc_rel",
                "pagina": 1,
                "texto": f"{conceito_a} ↔ {conceito_b}",
                "offsets": {"inicio": 0, "fim": 3},
                "caixas": [],
                "score_juiz": 0.65,
            }
        )
    else:
        eventos = []
        eventos.extend(list(fn(conceito_a, "A")))
        eventos.extend(list(fn(conceito_b, "B")))
        eventos.extend(list(fn(f"{conceito_a} {conceito_b}", "relacao")))

    return {
        "mensagem_id": mensagem_id,
        "lente": lente,
        "eventos": eventos,
        "papeis": ["A", "B", "relacao"],
    }


def lacunas(
    pedido: Mapping[str, Any],
    *,
    mensagem_id: str = "msg_lacunas",
    avaliar_linha: Callable[[str], Mapping[str, Any]] | None = None,
    escritor: EscritorChamado | None = None,
    escritor_chamado: MutableMapping[str, bool] | None = None,
) -> dict[str, Any]:
    """HTTP-lacunas: sem E2B. Uma mensagem com estado por linha."""
    linhas = pedido.get("linhas") or []
    if not isinstance(linhas, Sequence) or isinstance(linhas, (str, bytes)):
        return {"erro": "linhas_invalidas", "mensagem": "linhas deve ser uma lista."}
    limpas = [str(x).strip() for x in linhas if str(x).strip()]
    if not limpas:
        return {"erro": "linhas_em_falta", "mensagem": "É preciso pelo menos uma linha."}

    # Garantir que o escritor NÃO é chamado (REG-RES-011 / REG-BAR-010).
    if escritor is not None:
        # Lacunas recusa o escritor: não invocar.
        if escritor_chamado is not None:
            escritor_chamado["chamado"] = False

    itens: list[dict[str, Any]] = []
    for linha in limpas:
        if avaliar_linha is not None:
            itens.append(dict(avaliar_linha(linha)))
            continue
        # Mínimo: sem índice → ausente.
        itens.append({"linha": linha, "estado": "ausente", "citacao": None})

    return {
        "mensagem_id": mensagem_id,
        "lente": pedido.get("lente") or "acreditacao",
        "itens": itens,
        "escritor_chamado": False,
    }


def criar_alerta(
    pedido: Mapping[str, Any],
    *,
    alertas_existentes: int,
    limite: int = 10,
) -> dict[str, Any]:
    """Pedido de criação de alerta a partir da barra (HTTP-alerts-create).

    O motor completo é PLN-19; aqui só a validação de limite que a barra mostra.
    """
    texto = str(pedido.get("texto") or "").strip()
    if not texto:
        return {"erro": "texto_em_falta", "mensagem": "Texto do alerta em falta."}
    if alertas_existentes >= limite:
        return {
            "erro": "limite_alertas",
            "mensagem": "Máximo de dez alertas.",
            "http": 409,
        }
    return {
        "id": f"ale_{alertas_existentes + 1}",
        "chat_id": f"cht_al_{alertas_existentes + 1}",
        "activo": True,
        "http": 201,
    }


# --- HTTP (Starlette) -------------------------------------------------------

import json

from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route


def _json(corpo: dict, *, status: int = 200) -> Response:
    return Response(
        json.dumps(corpo, ensure_ascii=False).encode("utf-8"),
        status_code=status,
        media_type="application/json",
    )


async def http_correlate(request: Request) -> Response:
    try:
        pedido = await request.json()
    except Exception:
        return _json({"erro": "pedido_invalido", "mensagem": "JSON inválido."}, status=400)
    if not isinstance(pedido, dict):
        return _json({"erro": "pedido_invalido", "mensagem": "JSON inválido."}, status=400)
    r = correlacionar(pedido)
    if "erro" in r:
        return _json(r, status=400)
    return _json(r)


async def http_confront(request: Request) -> Response:
    try:
        pedido = await request.json()
    except Exception:
        return _json({"erro": "pedido_invalido", "mensagem": "JSON inválido."}, status=400)
    if not isinstance(pedido, dict):
        return _json({"erro": "pedido_invalido", "mensagem": "JSON inválido."}, status=400)
    r = confrontar(pedido)
    if "erro" in r:
        return _json(r, status=400)
    return _json(r)


async def http_lacunas(request: Request) -> Response:
    try:
        pedido = await request.json()
    except Exception:
        return _json({"erro": "pedido_invalido", "mensagem": "JSON inválido."}, status=400)
    if not isinstance(pedido, dict):
        return _json({"erro": "pedido_invalido", "mensagem": "JSON inválido."}, status=400)
    r = lacunas(pedido)
    if "erro" in r:
        return _json(r, status=400)
    return _json(r)


def rotas_modos() -> list[Route]:
    return [
        Route("/correlate", http_correlate, methods=["POST"]),
        Route("/confront", http_confront, methods=["POST"]),
        Route("/lacunas", http_lacunas, methods=["POST"]),
    ]
