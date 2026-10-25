"""Regressões REG-ALE-005, REG-ALE-006, REG-FOR-002 e retoma pós-pausa."""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Sequence
from unittest.mock import MagicMock

from engine.alertas.avaliar_documento import (
    avaliar_apos_indexacao,
    avaliar_documento_novo,
    em_idle,
)
from engine.alertas.criar import criar_alerta, definir_activo
from engine.juiz.pontuar import pontuar
from tests.alertas.apoio import (
    inserir_documento,
    inserir_frase,
    ligacao_migrada,
    mensagens_do_fio,
    meta_de,
)


class _JuizAlto:
    """Double: scores altos o suficiente para passar o limiar de teste."""

    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]:
        del pergunta
        return [0.95 for _ in frases]


class _JuizRegista:
    """Double que regista a pergunta recebida (para o prefixo da lente)."""

    def __init__(self) -> None:
        self.perguntas: list[str] = []

    def avaliar(self, pergunta: str, frases: Sequence[str]) -> list[float]:
        self.perguntas.append(pergunta)
        return [0.95 for _ in frases]


def test_reg_ale_005(caminho_tmp: Path) -> None:
    """Documento novo dispara mensagem com documento_id e miniatura; antigo/desligado não."""
    escritor = MagicMock()
    juiz = _JuizAlto()

    with ligacao_migrada(caminho_tmp) as ligacao:
        alerta = criar_alerta(ligacao, "menções a VPN", lente="investigar")
        doc_id = inserir_documento(
            ligacao,
            caminho="/tmp/novo-vpn.txt",
            miniatura="/tmp/mini-vpn.png",
        )
        inserir_frase(ligacao, doc_id, "Há novas menções a VPN na política.")
        ligacao.commit()

        criadas = avaliar_documento_novo(
            ligacao,
            doc_id,
            sessao=juiz,
            limiar=0.5,
            novo=True,
            escritor=escritor,
        )
        ligacao.commit()

        assert len(criadas) >= 1
        msgs = mensagens_do_fio(ligacao, alerta.conversa_id)
        assert len(msgs) == 1
        assert msgs[0]["modo"] == "alerta"
        meta = meta_de(msgs[0])
        assert meta["documento_id"] == doc_id
        assert meta["miniatura_caminho"] == "/tmp/mini-vpn.png"
        escritor.assert_not_called()

        # Reindexar o mesmo documento sem política «novo» → não dispara.
        n_antes = len(mensagens_do_fio(ligacao, alerta.conversa_id))
        avaliar_documento_novo(
            ligacao,
            doc_id,
            sessao=juiz,
            limiar=0.5,
            novo=False,
            escritor=escritor,
        )
        ligacao.commit()
        assert len(mensagens_do_fio(ligacao, alerta.conversa_id)) == n_antes

        # Alerta desligado → não dispara em documento novo.
        definir_activo(ligacao, alerta.id, False)
        doc2 = inserir_documento(
            ligacao,
            caminho="/tmp/outro.txt",
            miniatura="/tmp/mini-outro.png",
        )
        inserir_frase(ligacao, doc2, "Outra menção a VPN.")
        ligacao.commit()
        avaliar_documento_novo(
            ligacao,
            doc2,
            sessao=juiz,
            limiar=0.5,
            novo=True,
            escritor=escritor,
        )
        ligacao.commit()
        assert len(mensagens_do_fio(ligacao, alerta.conversa_id)) == n_antes

        # Sem escritor / resposta no caminho quente de avaliação.
        mod = importlib.import_module("engine.alertas.avaliar_documento")
        fonte = Path(mod.__file__).read_text(encoding="utf-8")
        assert "import engine.resposta" not in fonte
        assert "from engine.resposta" not in fonte
        assert "escritor" not in inspect.getsource(pontuar).casefold()
        escritor.assert_not_called()


def test_reg_ale_006(caminho_tmp: Path) -> None:
    """Alerta criado depois de docs antigos, sem documento novo, não relê a biblioteca."""
    juiz = _JuizAlto()
    with ligacao_migrada(caminho_tmp) as ligacao:
        antigo = inserir_documento(ligacao, caminho="/tmp/antigo.txt")
        inserir_frase(ligacao, antigo, "Contrato com cláusula de VPN.")
        ligacao.commit()

        alerta = criar_alerta(ligacao, "cláusula de VPN", lente="investigar")
        ligacao.commit()

        # Activo, mas sem documento novo a indexar → biblioteca antiga intacta no fio.
        em_idle(ligacao, sessao=juiz, limiar=0.5)
        ligacao.commit()
        assert mensagens_do_fio(ligacao, alerta.conversa_id) == []

        # Avaliar explicitamente o antigo como «não novo» também não escreve.
        avaliar_documento_novo(
            ligacao,
            antigo,
            sessao=juiz,
            limiar=0.5,
            novo=False,
        )
        ligacao.commit()
        assert mensagens_do_fio(ligacao, alerta.conversa_id) == []


def test_reg_for_002(caminho_tmp: Path) -> None:
    """Em idle, sem documento novo, não há job que reavalie sozinho a biblioteca."""
    juiz = _JuizAlto()
    with ligacao_migrada(caminho_tmp) as ligacao:
        for i in range(5):
            doc = inserir_documento(ligacao, caminho=f"/tmp/lib-{i}.txt")
            inserir_frase(ligacao, doc, f"Texto da biblioteca {i} com VPN.")
        alerta = criar_alerta(ligacao, "VPN", lente="investigar")
        ligacao.commit()

        em_idle(ligacao, sessao=juiz, limiar=0.5)
        em_idle(ligacao, sessao=juiz, limiar=0.5)
        ligacao.commit()
        assert mensagens_do_fio(ligacao, alerta.conversa_id) == []

        # A API pública não expõe varrimento completo.
        import engine.alertas as pacote

        assert not hasattr(pacote, "reavaliar_biblioteca")
        assert not hasattr(pacote, "varrer_biblioteca")


def test_avaliacao_apos_retoma_indexacao(caminho_tmp: Path) -> None:
    """Indexação pausada por procura não perde o gancho — avalia quando conclui."""
    juiz = _JuizAlto()
    with ligacao_migrada(caminho_tmp) as ligacao:
        alerta = criar_alerta(ligacao, "menções a VPN", lente="investigar")
        doc_id = inserir_documento(
            ligacao,
            caminho="/tmp/retoma.txt",
            miniatura="/tmp/mini-retoma.png",
            estado="a_indexar",
        )
        inserir_frase(ligacao, doc_id, "Há menções a VPN.")
        ligacao.commit()

        # Simula pausa (procura a decorrer): ainda não se avalia.
        assert mensagens_do_fio(ligacao, alerta.conversa_id) == []

        # Retoma e conclui a indexação → gancho pós-indexação.
        ligacao.execute(
            "UPDATE documentos SET estado = 'ok', indexado_em = criado_em "
            "WHERE id = ?",
            (doc_id,),
        )
        ligacao.commit()
        avaliar_apos_indexacao(
            ligacao,
            doc_id,
            sessao=juiz,
            limiar=0.5,
            foi_novo=True,
        )
        ligacao.commit()
        msgs = mensagens_do_fio(ligacao, alerta.conversa_id)
        assert len(msgs) == 1
        assert meta_de(msgs[0])["documento_id"] == doc_id


def test_lente_aplica_prefixo(caminho_tmp: Path) -> None:
    """A lente do alerta entra no texto enviado ao juiz (prefixo de tarefa)."""
    juiz = _JuizRegista()
    with ligacao_migrada(caminho_tmp) as ligacao:
        criar_alerta(ligacao, "Novas menções a VPN", lente="investigar")
        doc_id = inserir_documento(ligacao)
        inserir_frase(ligacao, doc_id, "Há menções a VPN.")
        ligacao.commit()

        avaliar_documento_novo(
            ligacao,
            doc_id,
            sessao=juiz,
            limiar=0.5,
            novo=True,
        )
        assert juiz.perguntas
        assert juiz.perguntas[0].startswith("task: question answering | query:")
        assert "Novas menções a VPN" in juiz.perguntas[0]
