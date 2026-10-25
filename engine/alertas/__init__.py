"""Alertas: até dez fios; juiz só em documentos novos indexados; sem E2B."""

from __future__ import annotations

from engine.alertas.avaliar_documento import (
    MensagemAlerta,
    avaliar_apos_indexacao,
    avaliar_documento_novo,
    em_idle,
)
from engine.alertas.criar import (
    PLACEHOLDER_VIGIA,
    Alerta,
    criar_alerta,
    definir_activo,
    listar_alertas,
)
from engine.alertas.limite import MAX_ALERTAS, LimiteAlertas
from engine.alertas.prefixos import consulta_com_prefixo

__all__ = [
    "MAX_ALERTAS",
    "PLACEHOLDER_VIGIA",
    "Alerta",
    "LimiteAlertas",
    "MensagemAlerta",
    "avaliar_apos_indexacao",
    "avaliar_documento_novo",
    "consulta_com_prefixo",
    "criar_alerta",
    "definir_activo",
    "em_idle",
    "listar_alertas",
]
