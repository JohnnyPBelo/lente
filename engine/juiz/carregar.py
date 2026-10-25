"""Carga da sessão ONNX Runtime int8 do juiz (thread-safe em ``run``)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from engine.juiz.caminhos import (
    MODELO_ID,
    caminho_onnx,
    ficheiro_onnx_maquina,
    identificar_modelo,
    pasta_juiz,
)


class DecisorRecusado(Exception):
    """Só o mmarco deste plano é aceite como decisor de highlight."""

    def __init__(self, modelo_id: str) -> None:
        self.modelo_id = modelo_id
        super().__init__(
            f"Decisor recusado: {modelo_id!r}. "
            f"O único identificador aceite é {MODELO_ID}."
        )


class PesosJuizAusentes(Exception):
    """Pesos ONNX em falta; a app pode abrir com caminho manual (PLN-21)."""

    def __init__(self, caminho_manual: str) -> None:
        self.caminho_manual = caminho_manual
        super().__init__(
            "Pesos do juiz ONNX ausentes. "
            f"Coloque o ficheiro int8 em: {caminho_manual}"
        )


def identificador_aceite() -> str:
    """Único modelo de decisão no âmbito do Lente."""
    return MODELO_ID


def validar_modelo_id(modelo_id: str) -> None:
    """Recusa Jev, Qwen, DeBERTa ou qualquer substituto do mmarco."""
    if modelo_id != MODELO_ID:
        raise DecisorRecusado(modelo_id)


@dataclass
class SessaoJuiz:
    """Sessão residente do cross-encoder ONNX.

    A ``InferenceSession`` do ONNX Runtime é segura para ``run`` concorrente
    na mesma instância; a carga e o fecho ficam no fio que gere o ciclo de vida.
    """

    modelo_id: str
    ficheiro_onnx: str
    runtime: str
    quantizacao: str
    caminho: Path
    _sessao: Any
    _tokenizador: Any | None = None

    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]:
        """Pontua pares (pergunta, frase) via ONNX; sem prosa."""
        from engine.juiz.pontuar import pontuar_com_sessao_onnx

        return pontuar_com_sessao_onnx(
            pergunta,
            frases,
            sessao_onnx=self._sessao,
            tokenizador=self._tokenizador,
        )


def carregar_sessao(
    *,
    raiz_modelos: Path | str | None = None,
    modelo_id: str = MODELO_ID,
    sessao_onnx: Any | None = None,
    tokenizador: Any | None = None,
) -> SessaoJuiz:
    """Carrega (ou aceita double de) sessão ONNX int8.

    Não descarrega pesos da rede. Se o ficheiro local faltar e não houver
    ``sessao_onnx`` injectada, levanta ``PesosJuizAusentes`` com o caminho manual.
    """
    validar_modelo_id(modelo_id)
    info = identificar_modelo()
    destino = caminho_onnx(raiz_modelos)

    if sessao_onnx is None:
        if not destino.is_file():
            raise PesosJuizAusentes(str(destino))
        import onnxruntime as ort

        # Sessão partilhável: InferenceSession.run é thread-safe.
        sessao_onnx = ort.InferenceSession(
            str(destino),
            providers=["CPUExecutionProvider"],
        )
        if tokenizador is None:
            tokenizador = _carregar_tokenizador(pasta_juiz(raiz_modelos))

    return SessaoJuiz(
        modelo_id=info.modelo_id,
        ficheiro_onnx=info.ficheiro_onnx,
        runtime=info.runtime,
        quantizacao=info.quantizacao,
        caminho=destino,
        _sessao=sessao_onnx,
        _tokenizador=tokenizador,
    )


def _carregar_tokenizador(pasta: Path) -> Any:
    """Tokenização alinhada ao Hugging Face original (ficheiros locais)."""
    caminho_json = pasta / "tokenizer.json"
    if not caminho_json.is_file():
        raise PesosJuizAusentes(str(caminho_json))
    from tokenizers import Tokenizer

    return Tokenizer.from_file(str(caminho_json))


def registar_versao(
    ligacao: sqlite3.Connection,
    *,
    revisao: str,
    ficheiro_onnx: str | None = None,
    notas: str | None = None,
) -> None:
    """Regista o juiz activo em ``versoes_modelo`` (desactiva o anterior)."""
    ficheiro = ficheiro_onnx or ficheiro_onnx_maquina()
    agora = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    texto_notas = notas or f"onnx int8: {ficheiro}"
    ligacao.execute(
        "UPDATE versoes_modelo SET activo = 0 WHERE papel = 'juiz' AND activo = 1"
    )
    ligacao.execute(
        "INSERT INTO versoes_modelo "
        "(papel, modelo_id, revisao, lora_id, activo, notas, registado_em) "
        "VALUES ('juiz', ?, ?, NULL, 1, ?, ?)",
        (MODELO_ID, revisao, texto_notas, agora),
    )
    ligacao.commit()
