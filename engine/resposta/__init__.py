"""Escritor E2B (visita) e filtro das duas portas."""

from __future__ import annotations

from engine.resposta.e2b import (
    ARTEFACTO_GGUF_Q4,
    MODELO_HF_ID,
    ArtefactoRecusado,
    EscritorE2B,
    PesosE2BAusentes,
    artefactos_aceites,
    caminho_gguf,
    validar_artefacto,
)
from engine.resposta.filtrar import (
    ResultadoParcial,
    ResultadoResposta,
    fechar_mensagem,
    filtrar_frases,
)
from engine.resposta.gerar import gerar_resposta, modo_chama_escritor
from engine.resposta.porta1_citacao import passar_porta1
from engine.resposta.porta2_fiel import passar_porta2
from engine.resposta.prompt import INSTRUCOES_LENTE, montar_contexto, texto_do_prompt
from engine.resposta.seguimento import reescrever_seguimento
from engine.resposta.tipos import (
    CandidatoCitado,
    Excerto,
    FraseAceite,
    Miniatura,
    PaginaAberta,
    TrechoPacote,
)

__all__ = [
    "ARTEFACTO_GGUF_Q4",
    "INSTRUCOES_LENTE",
    "MODELO_HF_ID",
    "ArtefactoRecusado",
    "CandidatoCitado",
    "EscritorE2B",
    "Excerto",
    "FraseAceite",
    "Miniatura",
    "PaginaAberta",
    "PesosE2BAusentes",
    "ResultadoParcial",
    "ResultadoResposta",
    "TrechoPacote",
    "artefactos_aceites",
    "caminho_gguf",
    "fechar_mensagem",
    "filtrar_frases",
    "gerar_resposta",
    "modo_chama_escritor",
    "montar_contexto",
    "passar_porta1",
    "passar_porta2",
    "reescrever_seguimento",
    "texto_do_prompt",
    "validar_artefacto",
]
