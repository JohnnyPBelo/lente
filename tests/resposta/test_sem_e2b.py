"""Regressão REG-RES-008: sem E2B devolve excertos e miniaturas sem cair."""

from __future__ import annotations

from engine.resposta.e2b import PesosE2BAusentes, EscritorE2B
from engine.resposta.gerar import gerar_resposta
from engine.resposta.tipos import Excerto, Miniatura, TrechoPacote


def test_reg_res_008(tmp_path) -> None:
    """E2B em falta + juiz disponível → excertos/miniaturas com offsets; sem prosa."""
    raiz = tmp_path / "models"
    (raiz / "e2b").mkdir(parents=True)

    trechos = [
        TrechoPacote(
            n=1,
            ficheiro="doc.pdf",
            pagina=2,
            texto="A política exige MFA no acesso remoto.",
            documento_id="doc_9",
            offset_inicio=40,
            offset_fim=80,
        )
    ]
    miniaturas = [
        Miniatura(documento_id="doc_9", pagina=2, caminho="thumbs/doc_9_p2.webp")
    ]
    excertos = [
        Excerto(
            n=1,
            documento_id="doc_9",
            pagina=2,
            texto=trechos[0].texto,
            offset_inicio=40,
            offset_fim=80,
        )
    ]

    escritor = EscritorE2B(raiz_modelos=raiz)
    assert escritor.disponivel() is False

    resultado = gerar_resposta(
        pergunta="O que exige a política?",
        trechos=trechos,
        modo="procurar",
        escritor=escritor,
        miniaturas=miniaturas,
        excertos=excertos,
        sessao_juiz=None,
    )

    assert resultado.frases == []
    assert len(resultado.excertos) == 1
    assert resultado.excertos[0].documento_id == "doc_9"
    assert resultado.excertos[0].offset_inicio == 40
    assert resultado.excertos[0].offset_fim == 80
    assert len(resultado.miniaturas) == 1
    assert resultado.miniaturas[0].documento_id == "doc_9"
    assert resultado.prosa_provisoria is False
    # Não cai: PesosE2BAusentes é tipado mas gerar_resposta degrada
    assert isinstance(PesosE2BAusentes("x"), Exception)
