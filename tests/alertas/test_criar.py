"""Regressões REG-ALE-001/003/004/007: criar, listar, fio e interruptor."""

from __future__ import annotations

from pathlib import Path

from engine.alertas.avaliar_documento import avaliar_documento_novo
from engine.alertas.criar import (
    PLACEHOLDER_VIGIA,
    criar_alerta,
    definir_activo,
    listar_alertas,
)
from tests.alertas.apoio import (
    inserir_documento,
    inserir_frase,
    ligacao_migrada,
    mensagens_do_fio,
)


def _copy_valor(chave: str) -> str:
    """Lê a string de docs/interface/copy.md pela chave da tabela."""
    texto = Path("docs/interface/copy.md").read_text(encoding="utf-8")
    for linha in texto.splitlines():
        if not linha.startswith("|"):
            continue
        partes = [p.strip() for p in linha.strip("|").split("|")]
        if len(partes) >= 2 and partes[0] == chave:
            return partes[1]
    raise AssertionError(f"chave ausente em copy.md: {chave}")


def test_reg_ale_001(caminho_tmp: Path) -> None:
    """Texto de vigilância com menos de dez alertas fica persistido; placeholder certo."""
    assert PLACEHOLDER_VIGIA == "O que queres que eu vigie?"
    assert PLACEHOLDER_VIGIA == _copy_valor("bar.alert.placeholder")

    with ligacao_migrada(caminho_tmp) as ligacao:
        alerta = criar_alerta(
            ligacao,
            "Novas menções a VPN",
            lente="investigar",
        )
        ligacao.commit()

        linha = ligacao.execute(
            "SELECT * FROM alertas WHERE id = ?",
            (alerta.id,),
        ).fetchone()
        assert linha is not None
        assert linha["consulta"] == "Novas menções a VPN"
        assert linha["activo"] == 1
        assert linha["lente"] == "investigar"
        assert linha["conversa_id"] == alerta.conversa_id


def test_reg_ale_003(caminho_tmp: Path) -> None:
    """Com alerta criado, a lista alimenta o grupo Alertas (rótulo de copy.md)."""
    # Sem apps/ui em main: o contrato de copy + listagem é a prova do grupo.
    assert _copy_valor("alerts.group") == "Alertas"
    assert _copy_valor("conversations.group") == "Conversas"

    with ligacao_migrada(caminho_tmp) as ligacao:
        criar_alerta(ligacao, "Novas menções a VPN", lente="investigar")
        ligacao.commit()
        listados = listar_alertas(ligacao)
        assert len(listados) >= 1
        assert listados[0].consulta == "Novas menções a VPN"


def test_reg_ale_004(caminho_tmp: Path) -> None:
    """Cada alerta tem fio (conversa) próprio, distinto de conversas de procura."""
    with ligacao_migrada(caminho_tmp) as ligacao:
        procura = ligacao.execute(
            "INSERT INTO conversas (titulo, criado_em, actualizado_em) "
            "VALUES ('Procura normal', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')"
        )
        conversa_procura = int(procura.lastrowid)

        alerta = criar_alerta(ligacao, "Vigiar contratos", lente="verificar")
        ligacao.commit()

        assert alerta.conversa_id != conversa_procura
        fio = ligacao.execute(
            "SELECT * FROM conversas WHERE id = ?",
            (alerta.conversa_id,),
        ).fetchone()
        assert fio is not None
        assert fio["apagada"] == 0

        # O fio do alerta não é a conversa de procura.
        ligacao_alerta = ligacao.execute(
            "SELECT conversa_id FROM alertas WHERE id = ?",
            (alerta.id,),
        ).fetchone()
        assert ligacao_alerta["conversa_id"] == alerta.conversa_id
        assert ligacao_alerta["conversa_id"] != conversa_procura


class _JuizAlto:
    def avaliar(self, pergunta: str, frases: list[str]) -> list[float]:
        del pergunta
        return [0.95 for _ in frases]


def test_reg_ale_007(caminho_tmp: Path) -> None:
    """Interruptor no fio (definir_activo) desliga emissões até voltar a ligar."""
    assert _copy_valor("alerts.toggle.on") == "Alerta ligado"
    assert _copy_valor("alerts.toggle.off") == "Alerta desligado"

    juiz = _JuizAlto()
    with ligacao_migrada(caminho_tmp) as ligacao:
        alerta = criar_alerta(ligacao, "menções a VPN", lente="investigar")
        ligacao.commit()

        desligado = definir_activo(ligacao, alerta.id, False)
        ligacao.commit()
        assert desligado.activo is False

        doc1 = inserir_documento(ligacao, caminho="/tmp/a.txt", miniatura="/tmp/a.png")
        inserir_frase(ligacao, doc1, "Há menções a VPN.")
        ligacao.commit()
        avaliar_documento_novo(
            ligacao, doc1, sessao=juiz, limiar=0.5, novo=True
        )
        ligacao.commit()
        assert mensagens_do_fio(ligacao, alerta.conversa_id) == []

        ligado = definir_activo(ligacao, alerta.id, True)
        ligacao.commit()
        assert ligado.activo is True

        doc2 = inserir_documento(ligacao, caminho="/tmp/b.txt", miniatura="/tmp/b.png")
        inserir_frase(ligacao, doc2, "Outras menções a VPN.")
        ligacao.commit()
        avaliar_documento_novo(
            ligacao, doc2, sessao=juiz, limiar=0.5, novo=True
        )
        ligacao.commit()
        assert len(mensagens_do_fio(ligacao, alerta.conversa_id)) == 1
