"""Discriminação de extensão / MIME e erros tipados de ingestão."""

from __future__ import annotations

from pathlib import Path


class FicheiroInexistente(Exception):
    """O caminho pedido não existe no disco (erro tipado, não genérico)."""

    def __init__(self, caminho: str) -> None:
        self.caminho = caminho
        super().__init__(f"Ficheiro inexistente: {caminho}")


class TipoNaoSuportado(Exception):
    """Extensão fora do âmbito deste plano (txt / md / docx)."""

    def __init__(self, caminho: str, extensao: str) -> None:
        self.caminho = caminho
        self.extensao = extensao
        super().__init__(
            f"Tipo não suportado nesta ingestão ({extensao or 'sem extensão'}): "
            f"{caminho}"
        )


def classificar(caminho: Path | str) -> str:
    """Devolve ``texto``, ``markdown`` ou ``docx`` conforme a extensão."""
    destino = Path(caminho)
    extensao = destino.suffix.lower()
    if extensao == ".txt":
        return "texto"
    if extensao in {".md", ".markdown"}:
        return "markdown"
    if extensao == ".docx":
        return "docx"
    raise TipoNaoSuportado(str(destino), extensao)
