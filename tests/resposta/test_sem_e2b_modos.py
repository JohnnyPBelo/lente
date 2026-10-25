"""Regressão REG-RES-011: alerta/lacunas sem E2B; lente só na prosa de procurar."""

from __future__ import annotations

from engine.resposta.gerar import gerar_resposta, modo_chama_escritor
from engine.resposta.prompt import INSTRUCOES_LENTE, montar_contexto, texto_do_prompt
from engine.resposta.tipos import TrechoPacote


class _EscritorEspiao:
    """Conta chamadas; não carrega GGUF."""

    def __init__(self) -> None:
        self.chamadas = 0
        self._residente = False

    def disponivel(self) -> bool:
        return True

    @property
    def residente(self) -> bool:
        return self._residente

    def carregar(self) -> None:
        self._residente = True

    def gerar(self, prompt: str) -> str:
        del prompt
        self.chamadas += 1
        return "Prosa que não deveria existir em alerta. [1]"

    def libertar(self) -> None:
        self._residente = False


def test_reg_res_011() -> None:
    """Alerta e lacunas não chamam o escritor; procurar com lente mete instrução."""
    assert modo_chama_escritor("alerta") is False
    assert modo_chama_escritor("lacunas") is False
    assert modo_chama_escritor("procurar") is True
    assert modo_chama_escritor("correlacionar") is True

    trechos = [
        TrechoPacote(
            n=1,
            ficheiro="a.pdf",
            pagina=1,
            texto="Frase nova indexada.",
            documento_id="doc_1",
        )
    ]
    espiao = _EscritorEspiao()

    for modo in ("alerta", "lacunas"):
        resultado = gerar_resposta(
            pergunta="avisar novidades",
            trechos=trechos,
            modo=modo,
            escritor=espiao,
            miniaturas=[],
            excertos=[],
            sessao_juiz=None,
        )
        assert espiao.chamadas == 0
        assert resultado.frases == []
        assert espiao.residente is False

    pacote = montar_contexto(
        trechos,
        pergunta="O que diz o documento?",
        lente="investigar",
    )
    texto = texto_do_prompt(pacote)
    instrucao = INSTRUCOES_LENTE["investigar"]
    assert "Responde em português de Portugal" in texto
    assert "trechos numerados" in texto.casefold() or "citação" in texto.casefold()
    # Distinta dos prefixos de embedding (task: search result / question answering)
    assert "task: search result" not in texto
    assert "task: question answering" not in texto
    assert instrucao.splitlines()[0] in texto
