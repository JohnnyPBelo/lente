"""Regressões de exportar/importar correções JSON (PLN-17)."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

import pytest

from engine.armazenamento.repositorio import abrir
from engine.escalonador.slot import SlotPesado
from engine.feedback.registar import hash_par, listar_pares, registar_acertou
from engine.juiz.caminhos import MODELO_ID

RAIZ = Path(__file__).resolve().parents[2]
ESQUEMA = RAIZ / "docs" / "dados" / "correcoes.schema.json"
FIXTURE = RAIZ / "tests" / "fixtures" / "feedback" / "correcoes.exemplo.json"


def _carregar_esquema() -> dict[str, Any]:
    return json.loads(ESQUEMA.read_text(encoding="utf-8"))


def _validar_contra_esquema(dados: dict[str, Any]) -> None:
    from tests.regressao.apoio import validar_instancia

    validar_instancia(dados, _carregar_esquema(), "$")


def _pacote_sintetico(*, modelo: str = MODELO_ID) -> dict[str, Any]:
    pergunta = "Quem aprova o acesso remoto?"
    trecho = "O acesso remoto exige aprovação do responsável de segurança."
    etiqueta = "positivo"
    lente = "investigar"
    return {
        "format_version": "1",
        "base_model_id": modelo,
        "corrections": [
            {
                "pergunta": pergunta,
                "trecho": trecho,
                "etiqueta": etiqueta,
                "lente": lente,
                "hash_par": hash_par(pergunta, trecho, etiqueta, lente),
            }
        ],
    }


class _TreinadorDuplo:
    """Double de treino: regista pares e cede o slot à procura."""

    def __init__(self, slot: SlotPesado) -> None:
        self.slot = slot
        self.torch_presente = False
        self.pares_vistos: list[dict[str, Any]] = []
        self.rank: int | None = None

    def carregar_pytorch(self) -> None:
        self.torch_presente = True

    def libertar(self) -> None:
        self.torch_presente = False

    def treinar(
        self,
        pares: list[dict[str, Any]],
        *,
        rank: int,
        learning_rate: float,
        pull_to_base: float,
        nucleos: int,
    ) -> dict[str, Any]:
        del learning_rate, pull_to_base, nucleos
        self.pares_vistos = list(pares)
        self.rank = rank
        # Simula procura a chegar a meio do treino.
        def _procurar() -> None:
            with self.slot.antes_de_procurar():
                pass

        t = threading.Thread(target=_procurar)
        t.start()
        self.slot.ponto_de_pausa()
        t.join(timeout=2.0)
        return {
            "adaptador_id": "lora-teste",
            "metrica_holdout_base": 0.5,
            "metrica_holdout": 0.6,
        }


def test_reg_fbk_011(caminho_tmp) -> None:
    """Dois pares com o mesmo hash contam uma vez no conjunto."""
    from engine.feedback.exportar_correcoes import deduplicar_correcoes

    pergunta = "Quem aprova o acesso remoto?"
    trecho = "O acesso remoto exige aprovação do responsável de segurança."
    digest = hash_par(pergunta, trecho, "positivo", "investigar")
    pares = [
        {
            "pergunta": pergunta,
            "trecho": trecho,
            "etiqueta": "positivo",
            "lente": "investigar",
            "hash_par": digest,
        },
        {
            "pergunta": pergunta,
            "trecho": trecho,
            "etiqueta": "positivo",
            "lente": "investigar",
            "hash_par": digest,
        },
    ]
    unicos = deduplicar_correcoes(pares)
    assert len(unicos) == 1
    assert unicos[0]["hash_par"] == digest


def test_reg_fbk_012(caminho_tmp) -> None:
    """Export é JSON aceite pelo esquema; sem pesos."""
    from engine.feedback.exportar_correcoes import exportar_correcoes

    ligacao = abrir(caminho_tmp)
    registar_acertou(
        ligacao,
        mensagem_id=None,
        pergunta="Quem aprova o acesso remoto?",
        trechos_mostrados=[
            "O acesso remoto exige aprovação do responsável de segurança."
        ],
        lente="investigar",
    )

    dados = exportar_correcoes(ligacao)
    _validar_contra_esquema(dados)
    assert dados["format_version"] == "1"
    assert dados["base_model_id"] == MODELO_ID
    assert dados["corrections"]
    for correcao in dados["corrections"]:
        assert set(correcao) >= {
            "pergunta",
            "trecho",
            "etiqueta",
            "lente",
            "hash_par",
        }
    texto = json.dumps(dados)
    for proibido in (".safetensors", ".onnx", ".pt", "lora_weights", "state_dict"):
        assert proibido not in texto


def test_reg_fbk_014(caminho_tmp) -> None:
    """Preview sem confirmar não grava; com confirmar grava e agenda treino."""
    from engine.feedback.importar_correcoes import importar_correcoes
    from engine.feedback.lora import treinar_lora

    ligacao = abrir(caminho_tmp)
    pacote = _pacote_sintetico()
    agendamentos: list[str] = []

    def _agendar() -> None:
        agendamentos.append("treino")

    previa = importar_correcoes(
        ligacao,
        pacote,
        confirmar=False,
        agendar_treino=_agendar,
    )
    assert previa["contagem"] == 1
    assert "investigar" in previa["lentes"]
    assert previa["amostra_perguntas"]
    assert previa["modelo_base_ok"] is True
    assert listar_pares(ligacao) == []
    assert agendamentos == []

    resultado = importar_correcoes(
        ligacao,
        pacote,
        confirmar=True,
        agendar_treino=_agendar,
    )
    assert resultado["aceite"] is True
    assert resultado["treino_agendado"] is True
    assert len(listar_pares(ligacao)) == 1
    assert agendamentos == ["treino"]

    # Segundo import não duplica hashes.
    importar_correcoes(
        ligacao,
        pacote,
        confirmar=True,
        agendar_treino=_agendar,
    )
    assert len(listar_pares(ligacao)) == 1

    # O pipeline de treino (PLN-16) consome o conjunto.
    slot = SlotPesado()
    treinador = _TreinadorDuplo(slot)
    treinar_lora(ligacao, slot=slot, treinador=treinador)
    assert len(treinador.pares_vistos) == 1


def test_reg_fbk_015(caminho_tmp) -> None:
    """Ficheiro de outro modelo base é recusado."""
    from engine.feedback.importar_correcoes import (
        ModeloBaseIncompativel,
        importar_correcoes,
    )

    ligacao = abrir(caminho_tmp)
    pacote = _pacote_sintetico(modelo="outro/modelo-base")
    with pytest.raises(ModeloBaseIncompativel):
        importar_correcoes(ligacao, pacote, confirmar=True)
    assert listar_pares(ligacao) == []


def test_reg_fbk_016(caminho_tmp) -> None:
    """JSON inválido ou por confirmar não altera o juiz."""
    from engine.feedback.importar_correcoes import (
        CorrecoesInvalidas,
        importar_correcoes,
    )

    ligacao = abrir(caminho_tmp)
    registar_acertou(
        ligacao,
        mensagem_id=None,
        pergunta="Pergunta estável",
        trechos_mostrados=["Trecho estável."],
        lente="verificar",
    )
    antes = listar_pares(ligacao)

    # Invertia etiquetas: ainda sem confirmar → sem escrita.
    malicioso = _pacote_sintetico()
    malicioso["corrections"][0]["etiqueta"] = "negativo"
    malicioso["corrections"][0]["hash_par"] = hash_par(
        malicioso["corrections"][0]["pergunta"],
        malicioso["corrections"][0]["trecho"],
        "negativo",
        malicioso["corrections"][0]["lente"],
    )
    importar_correcoes(ligacao, malicioso, confirmar=False)
    assert listar_pares(ligacao) == antes

    with pytest.raises(CorrecoesInvalidas):
        importar_correcoes(ligacao, {"format_version": "9"}, confirmar=True)
    assert listar_pares(ligacao) == antes


def test_reg_fbk_018(caminho_tmp) -> None:
    """Treino parte do base, une locais+importadas sem hashes repetidos; pausável."""
    from engine.feedback.importar_correcoes import importar_correcoes
    from engine.feedback.lora import RANK, treinar_lora
    from engine.juiz.caminhos import MODELO_ID as BASE

    ligacao = abrir(caminho_tmp)
    registar_acertou(
        ligacao,
        mensagem_id=None,
        pergunta="Pergunta local",
        trechos_mostrados=["Trecho local positivo."],
        lente="investigar",
    )
    pacote = _pacote_sintetico()
    # Mesmo hash que um local + um novo: o import não duplica.
    importar_correcoes(ligacao, pacote, confirmar=True, agendar_treino=lambda: None)

    hashes = {p["hash_par"] for p in listar_pares(ligacao)}
    assert len(hashes) == len(listar_pares(ligacao))

    slot = SlotPesado(onnx_activo="onnx_base")
    treinador = _TreinadorDuplo(slot)
    # holdout_fraccao=0: o conjunto união (sem hashes repetidos) entra no treino.
    resultado = treinar_lora(
        ligacao, slot=slot, treinador=treinador, holdout_fraccao=0.0
    )

    assert resultado["aceite"] is True
    assert treinador.rank == RANK
    assert BASE == MODELO_ID  # parte do modelo base, não média de adapters
    vistos = {p["hash_par"] for p in treinador.pares_vistos}
    assert vistos == hashes
    assert slot.pausas_observadas >= 1


def test_reg_seg_004(caminho_tmp) -> None:
    """Confirmação falsa ou omissa não acrescenta linhas."""
    from engine.feedback.importar_correcoes import importar_correcoes

    ligacao = abrir(caminho_tmp)
    pacote = _pacote_sintetico()
    importar_correcoes(ligacao, pacote, confirmar=False)
    assert listar_pares(ligacao) == []
    # omissão de confirmar → default False
    importar_correcoes(ligacao, pacote)
    assert listar_pares(ligacao) == []


def test_reg_for_003(caminho_tmp) -> None:
    """Só JSON de correções; binário LoRA não é aceite como junção."""
    from engine.feedback.exportar_correcoes import exportar_correcoes
    from engine.feedback.importar_correcoes import (
        CorrecoesInvalidas,
        importar_correcoes,
    )

    ligacao = abrir(caminho_tmp)
    # Binário / média de pesos oferecida como «afinação».
    with pytest.raises(CorrecoesInvalidas):
        importar_correcoes(
            ligacao,
            {
                "format_version": "1",
                "base_model_id": MODELO_ID,
                "lora_adapters": [{"weights": "AAAA"}],
                "corrections": [],
            },
            confirmar=True,
        )
    with pytest.raises(CorrecoesInvalidas):
        importar_correcoes(
            ligacao,
            b"\x00\x01LORA_BINARIO_FALSO",
            confirmar=True,
        )

    dados = exportar_correcoes(ligacao)
    assert "corrections" in dados
    assert "lora_adapters" not in dados
    assert "weights" not in json.dumps(dados)


def test_export_import_ciclo_fixture(caminho_tmp) -> None:
    """Fixture sintética valida; confirmar grava; segundo import dedupe."""
    from engine.feedback.importar_correcoes import (
        ModeloBaseIncompativel,
        importar_correcoes,
    )

    ligacao = abrir(caminho_tmp)
    pacote = json.loads(FIXTURE.read_text(encoding="utf-8"))
    _validar_contra_esquema(pacote)

    importar_correcoes(ligacao, pacote, confirmar=False)
    assert listar_pares(ligacao) == []

    importar_correcoes(ligacao, pacote, confirmar=True, agendar_treino=lambda: None)
    assert len(listar_pares(ligacao)) == len(pacote["corrections"])

    importar_correcoes(ligacao, pacote, confirmar=True, agendar_treino=lambda: None)
    assert len(listar_pares(ligacao)) == len(pacote["corrections"])

    outro = dict(pacote)
    outro["base_model_id"] = "modelo/diferente"
    with pytest.raises(ModeloBaseIncompativel):
        importar_correcoes(ligacao, outro, confirmar=True)
