"""OCR via Tesseract (única dependência de sistema).

Instalação típica (Debian/Ubuntu)::

    sudo apt-get install -y tesseract-ocr tesseract-ocr-por

Idioma por omissão: ``por``. Sem o binário, as funções levantam
``TesseractEmFalta`` — nunca um índice vazio em silêncio.

As caixas seguem o contrato de ``frases.caixas_json``:
``{pagina, x, y, largura, altura}`` (origem no canto superior esquerdo da
imagem, unidades em píxeis da página rasterizada).
"""

from __future__ import annotations

import csv
import io
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from engine.ingestao.imagens import raster_para_ocr

_IDIOMA_OMISSAO = "por"
_TIMEOUT_OMISSAO = 60.0


class TesseractEmFalta(Exception):
    """O binário ``tesseract`` não está disponível no PATH."""

    def __init__(self) -> None:
        super().__init__(
            "Tesseract em falta: instale tesseract-ocr e o idioma por "
            "(ex.: tesseract-ocr-por). Sem OCR não se indexa o scan."
        )


@dataclass(frozen=True)
class ResultadoOCR:
    """Texto reconhecido e caixas aproximadas por palavra."""

    texto: str
    caixas: list[dict[str, float | int]] = field(default_factory=list)
    estado: str = "ok"


def caminho_tesseract() -> str | None:
    """Caminho do executável, ou ``None`` se ausente."""
    return shutil.which("tesseract")


def _exigir_binario() -> str:
    binario = caminho_tesseract()
    if binario is None:
        raise TesseractEmFalta()
    return binario


def _parse_tsv(tsv: str, *, pagina: int) -> ResultadoOCR:
    leitor = csv.DictReader(io.StringIO(tsv), delimiter="\t")
    palavras: list[str] = []
    caixas: list[dict[str, float | int]] = []
    for linha in leitor:
        try:
            nivel = int(linha.get("level") or 0)
        except ValueError:
            continue
        # nível 5 = palavra no TSV do Tesseract
        if nivel != 5:
            continue
        texto = (linha.get("text") or "").strip()
        if not texto:
            continue
        try:
            largura = float(linha.get("width") or 0)
            altura = float(linha.get("height") or 0)
            x = float(linha.get("left") or 0)
            y = float(linha.get("top") or 0)
        except ValueError:
            continue
        palavras.append(texto)
        if largura > 0 and altura > 0:
            caixas.append(
                {
                    "pagina": pagina,
                    "x": x,
                    "y": y,
                    "largura": largura,
                    "altura": altura,
                }
            )
    texto_final = " ".join(palavras).strip()
    estado = "ok" if texto_final else "aviso"
    return ResultadoOCR(texto=texto_final, caixas=caixas, estado=estado)


def ocr_imagem(
    caminho: Path | str,
    *,
    pagina: int = 1,
    idioma: str = _IDIOMA_OMISSAO,
    timeout: float = _TIMEOUT_OMISSAO,
) -> ResultadoOCR:
    """Corre Tesseract sobre uma imagem; devolve texto e caixas por palavra."""
    binario = _exigir_binario()
    destino = raster_para_ocr(caminho)
    try:
        concluido = subprocess.run(
            [
                binario,
                str(destino),
                "stdout",
                "-l",
                idioma,
                "tsv",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as erro:
        raise TimeoutError(
            f"Tesseract excedeu {timeout}s em {destino}"
        ) from erro
    except FileNotFoundError as erro:
        raise TesseractEmFalta() from erro

    if concluido.returncode != 0:
        stderr = (concluido.stderr or "").strip()
        raise RuntimeError(
            f"Tesseract falhou ({concluido.returncode}) em {destino}: {stderr}"
        )

    return _parse_tsv(concluido.stdout or "", pagina=pagina)


__all__ = [
    "ResultadoOCR",
    "TesseractEmFalta",
    "caminho_tesseract",
    "ocr_imagem",
]
