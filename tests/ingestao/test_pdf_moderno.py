"""Regressão: PDFs modernos (catálogo ≠ obj 1, streams comprimidos).

Cobre o falhanço «PDF sem /Pages» visto com reportlab e GovInfo (#66).
"""

from __future__ import annotations

import zlib
from pathlib import Path
from unittest.mock import patch

FRASE = "Texto reportlab sintetica para regressao PDF."


def _pdf_catalogo_deslocado_flate(frase: str = FRASE) -> bytes:
    """PDF clássico com /Root≠1 e Contents em FlateDecode (estilo reportlab)."""
    # Objectos: 1=font resources, 2=font, 3=page, 4=catalog, 5=pages, 6=contents
    fluxo = (
        f"BT /F1 12 Tf 1 0 0 1 72 720 Tm ({frase}) Tj ET"
    ).encode("latin-1")
    comprimido = zlib.compress(fluxo)
    objectos: list[bytes] = [
        b"<< /F1 2 0 R >>",  # 1 — NÃO é Catalog (bug antigo assumia obj 1)
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"",  # 3 page — preenchido abaixo
        b"<< /Type /Catalog /Pages 5 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            f"<< /Filter /FlateDecode /Length {len(comprimido)} >>\nstream\n".encode()
            + comprimido
            + b"\nendstream"
        ),
    ]
    objectos[2] = (
        b"<< /Type /Page /Parent 5 0 R /MediaBox [0 0 612 792] "
        b"/Contents 6 0 R "
        b"/Resources << /Font 1 0 R >> >>"
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
        f"trailer\n<< /Size {len(objectos) + 1} /Root 4 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n"
    ).encode()
    return bytes(saida)


def test_stdlib_pdf_catalogo_deslocado_e_flate(tmp_path: Path) -> None:
    """Stdlib encontra /Pages via /Root e lê stream FlateDecode."""
    from engine.ingestao import pdf as pdf_mod

    destino = tmp_path / "moderno_flate.pdf"
    destino.write_bytes(_pdf_catalogo_deslocado_flate())

    resultado = pdf_mod._extrair_com_stdlib(destino)
    assert len(resultado.paginas) == 1
    assert FRASE in resultado.texto
    assert resultado.precisa_ocr is False


def test_extrair_pdf_moderno_nao_levanta_sem_pages(tmp_path: Path) -> None:
    """``extrair_pdf`` (pypdf ou stdlib) aceita PDF com Root≠1."""
    from engine.ingestao.pdf import extrair_pdf

    destino = tmp_path / "moderno.pdf"
    destino.write_bytes(_pdf_catalogo_deslocado_flate())
    resultado = extrair_pdf(destino)
    assert FRASE in resultado.texto
    assert resultado.precisa_ocr is False


def test_extrair_pdf_reportlab_se_disponivel(tmp_path: Path) -> None:
    """Se reportlab estiver instalado, o PDF gerado deixa de falhar com /Pages."""
    try:
        from reportlab.pdfgen import canvas
    except ImportError:
        return

    from engine.ingestao import pdf as pdf_mod
    from engine.ingestao.pdf import extrair_pdf

    destino = tmp_path / "reportlab.pdf"
    c = canvas.Canvas(str(destino))
    c.drawString(72, 720, FRASE)
    c.save()

    # Caminho stdlib (sem depender de pypdf no CI mínimo).
    with patch.object(pdf_mod, "_PYPDF_DISPONIVEL", False):
        so_stdlib = extrair_pdf(destino)
    assert FRASE in so_stdlib.texto

    completo = extrair_pdf(destino)
    assert FRASE in completo.texto
