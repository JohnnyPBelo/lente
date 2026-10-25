"""Exportação atómica do ONNX do juiz após LoRA aceite."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from engine.escalonador.slot import SlotPesado
from engine.juiz.caminhos import MODELO_ID


def _agora() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def exportar_onnx_atomico(
    *,
    destino: Path | str,
    adaptador_id: str,
    ligacao: sqlite3.Connection,
    slot: SlotPesado,
    escritor: Callable[[Path], None] | None = None,
) -> Path:
    """Escreve o ONNX novo, actualiza ``versoes_modelo`` e só então activa o slot.

    Até esta função correr com sucesso, a procura continua no ONNX anterior.
    """
    caminho = Path(destino)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(caminho.suffix + ".tmp")

    def _escrever_omissao(p: Path) -> None:
        p.write_bytes(b"")

    (escritor or _escrever_omissao)(temporario)
    temporario.replace(caminho)

    ligacao.execute(
        "UPDATE versoes_modelo SET activo = 0 WHERE papel = 'juiz' AND activo = 1"
    )
    ligacao.execute(
        "INSERT INTO versoes_modelo "
        "(papel, modelo_id, revisao, lora_id, activo, notas, registado_em) "
        "VALUES ('juiz', ?, ?, ?, 1, ?, ?)",
        (
            MODELO_ID,
            caminho.name,
            adaptador_id,
            f"onnx após LoRA {adaptador_id}",
            _agora(),
        ),
    )
    ligacao.commit()

    # Só depois do export e do registo a procura muda de modelo.
    slot.definir_onnx_activo(str(caminho))
    return caminho
