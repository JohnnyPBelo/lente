"""Discriminação de extensão / MIME e erros tipados de ingestão."""

from __future__ import annotations

from pathlib import Path


class FicheiroInexistente(Exception):
    """O caminho pedido não existe no disco (erro tipado, não genérico)."""

    def __init__(self, caminho: str) -> None:
        self.caminho = caminho
        super().__init__(f"Ficheiro inexistente: {caminho}")


class TipoNaoSuportado(Exception):
    """Extensão fora do âmbito desta ingestão."""

    def __init__(self, caminho: str, extensao: str) -> None:
        self.caminho = caminho
        self.extensao = extensao
        super().__init__(
            f"Tipo não suportado nesta ingestão ({extensao or 'sem extensão'}): "
            f"{caminho}"
        )


def classificar(caminho: Path | str) -> str:
    """Devolve o tipo lógico conforme a extensão."""
    destino = Path(caminho)
    extensao = destino.suffix.lower()
    if extensao == ".txt":
        return "texto"
    if extensao in {".md", ".markdown"}:
        return "markdown"
    if extensao == ".docx":
        return "docx"
    if extensao == ".pdf":
        return "pdf"
    if extensao in {".png", ".jpg", ".jpeg", ".webp"}:
        return "imagem"
    raise TipoNaoSuportado(str(destino), extensao)
