"""Regressões REG-ALE-001 e REG-ALE-004: criar alerta e fio próprio."""

from __future__ import annotations

from pathlib import Path

from engine.alertas.criar import PLACEHOLDER_VIGIA, criar_alerta
from tests.alertas.apoio import ligacao_migrada


def test_reg_ale_001(caminho_tmp: Path) -> None:
    """Texto de vigilância com menos de dez alertas fica persistido; placeholder certo."""
    assert PLACEHOLDER_VIGIA == "O que queres que eu vigie?"

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
