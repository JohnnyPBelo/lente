"""Regressão REG-ING-005: PDF com texto seleccionável, caixas e precisa_ocr."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

FIXTORES = Path(__file__).resolve().parents[1] / "fixtures" / "ingestao"
FRASE_AMOSTRA = "A frase sintetica da amostra PDF fica nesta linha."


def _escapar_pdf(texto: str) -> str:
    return texto.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _construir_pdf_texto(
    paginas: list[list[tuple[str, float, float, float]]],
) -> bytes:
    """PDF mínimo sintético: cada página é lista de (texto, x, y, tamanho)."""
    objectos: list[bytes] = []

    def acrescentar(corpo: bytes) -> int:
        objectos.append(corpo)
        return len(objectos)

    acrescentar(b"")  # 1 Catalog
    acrescentar(b"")  # 2 Pages
    kids: list[tuple[int, int]] = []
    for operacoes in paginas:
        linhas = ["BT"]
        for texto, x, y, tamanho in operacoes:
            linhas.append(f"/F1 {tamanho:g} Tf")
            linhas.append(f"1 0 0 1 {x:g} {y:g} Tm")
            linhas.append(f"({_escapar_pdf(texto)}) Tj")
        linhas.append("ET")
        fluxo = "\n".join(linhas).encode("latin-1")
        conteudo_id = acrescentar(
            f"<< /Length {len(fluxo)} >>\nstream\n".encode()
            + fluxo
            + b"\nendstream"
        )
        pagina_id = acrescentar(b"")
        kids.append((pagina_id, conteudo_id))

    fonte_id = acrescentar(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for pagina_id, conteudo_id in kids:
        objectos[pagina_id - 1] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Contents {conteudo_id} 0 R "
            f"/Resources << /Font << /F1 {fonte_id} 0 R >> >> >>"
        ).encode()

    kids_txt = " ".join(f"{pid} 0 R" for pid, _ in kids)
    objectos[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objectos[1] = (
        f"<< /Type /Pages /Kids [{kids_txt}] /Count {len(kids)} >>"
    ).encode()

    saida = bytearray(b"%PDF-1.4\n")
    deslocamentos = [0]
    for indice, corpo in enumerate(objectos, start=1):
        deslocamentos.append(len(saida))
        saida += f"{indice} 0 obj\n".encode()
        saida += corpo
        saida += b"\nendobj\n"
    xref = len(saida)
    saida += f"xref\n0 {len(objectos) + 1}\n".encode()
    saida += b"0000000000 65535 f \n"
    for deslocamento in deslocamentos[1:]:
        saida += f"{deslocamento:010d} 00000 n \n".encode()
    saida += (
        f"trailer\n<< /Size {len(objectos) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n"
    ).encode()
    return bytes(saida)


def _construir_pdf_so_imagem() -> bytes:
    """PDF de uma página com XObject imagem e sem operadores de texto."""
    # Imagem 1x1 cinzenta em raw.
    imagem = bytes([128])
    objectos: list[bytes] = []

    def acrescentar(corpo: bytes) -> int:
        objectos.append(corpo)
        return len(objectos)

    acrescentar(b"<< /Type /Catalog /Pages 2 0 R >>")
    acrescentar(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    acrescentar(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R "
        b"/Resources << /XObject << /Im1 5 0 R >> >> >>"
    )
    fluxo = b"q\n612 0 0 792 0 0 cm\n/Im1 Do\nQ"
    acrescentar(f"<< /Length {len(fluxo)} >>\nstream\n".encode() + fluxo + b"\nendstream")
    acrescentar(
        f"<< /Type /XObject /Subtype /Image /Width 1 /Height 1 "
        f"/ColorSpace /DeviceGray /BitsPerComponent 8 "
        f"/Length {len(imagem)} >>\nstream\n".encode()
        + imagem
        + b"\nendstream"
    )

    saida = bytearray(b"%PDF-1.4\n")
    deslocamentos = [0]
    for indice, corpo in enumerate(objectos, start=1):
        deslocamentos.append(len(saida))
        saida += f"{indice} 0 obj\n".encode()
        saida += corpo
        saida += b"\nendobj\n"
    xref = len(saida)
    saida += f"xref\n0 {len(objectos) + 1}\n".encode()
    saida += b"0000000000 65535 f \n"
    for deslocamento in deslocamentos[1:]:
        saida += f"{deslocamento:010d} 00000 n \n".encode()
    saida += (
        f"trailer\n<< /Size {len(objectos) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n"
    ).encode()
    return bytes(saida)


def test_reg_ing_005(tmp_path: Path) -> None:
    """PDF com texto/caixas; só imagem → precisa_ocr; multipágina com pagina certa."""
    from engine.ingestao.pdf import extrair_pdf

    amostra = FIXTORES / "amostra_texto.pdf"
    resultado = extrair_pdf(amostra)
    assert len(resultado.paginas) >= 1
    texto_junto = "\n".join(p.texto for p in resultado.paginas)
    assert FRASE_AMOSTRA in texto_junto
    assert resultado.precisa_ocr is False

    caixa_ok = False
    for pagina in resultado.paginas:
        for span in pagina.spans:
            if FRASE_AMOSTRA in span.texto or span.texto in FRASE_AMOSTRA:
                caixa = span.caixa
                if (
                    caixa.pagina == 1
                    and caixa.largura > 0
                    and caixa.altura > 0
                ):
                    caixa_ok = True
                    break
        if caixa_ok:
            break
    assert caixa_ok, "esperava caixa na página 1 alinhada à frase da fixture"

    so_imagem = tmp_path / "so_imagem.pdf"
    so_imagem.write_bytes(_construir_pdf_so_imagem())
    with patch("subprocess.run") as corrido, patch(
        "subprocess.Popen"
    ) as aberto:
        sem_texto = extrair_pdf(so_imagem)
        assert sem_texto.precisa_ocr is True
        assert all(not p.texto.strip() for p in sem_texto.paginas)
        corrido.assert_not_called()
        aberto.assert_not_called()
    assert "engine.ingestao.ocr" not in __import__("sys").modules

    multi = tmp_path / "multi.pdf"
    multi.write_bytes(
        _construir_pdf_texto(
            [
                [("Texto da pagina um sintetica.", 72, 720, 12)],
                [("Texto da pagina dois sintetica.", 72, 700, 12)],
            ]
        )
    )
    varias = extrair_pdf(multi)
    assert len(varias.paginas) == 2
    paginas_caixas = {span.caixa.pagina for p in varias.paginas for span in p.spans}
    assert 1 in paginas_caixas
    assert 2 in paginas_caixas
    for pagina in varias.paginas:
        for span in pagina.spans:
            assert span.caixa.pagina == pagina.numero
