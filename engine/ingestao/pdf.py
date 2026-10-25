"""Extracção de PDF com camada de texto: páginas, spans e caixas.

Implementação em stdlib (sem pypdf/PyMuPDF): o CI só instala pytest, como no
docx. Quando existir ``pyproject.toml``, uma biblioteca BSD/MIT (ex. pypdf,
BSD) pode substituir este leitor mínimo. Coordenadas: origem no canto
inferior esquerdo, pontos PDF (1/72").

Não chama Tesseract: PDF sem texto seleccionável marca ``precisa_ocr=True``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from engine.ingestao.caixas import Caixa
from engine.ingestao.paginas import PaginaExtraida, SpanExtraido
from engine.ingestao.tipos import FicheiroInexistente

# Larguras aproximadas Helvetica (WinAnsi) em milésimos da unidade em.
_LARGURA_HELVETICA: dict[str, int] = {
    " ": 278,
    "!": 278,
    '"': 355,
    "#": 556,
    "$": 556,
    "%": 889,
    "&": 667,
    "'": 191,
    "(": 333,
    ")": 333,
    "*": 389,
    "+": 584,
    ",": 278,
    "-": 333,
    ".": 278,
    "/": 278,
    "0": 556,
    "1": 556,
    "2": 556,
    "3": 556,
    "4": 556,
    "5": 556,
    "6": 556,
    "7": 556,
    "8": 556,
    "9": 556,
    ":": 278,
    ";": 278,
    "<": 584,
    "=": 584,
    ">": 584,
    "?": 556,
    "@": 1015,
    "A": 667,
    "B": 667,
    "C": 722,
    "D": 722,
    "E": 667,
    "F": 611,
    "G": 778,
    "H": 722,
    "I": 278,
    "J": 500,
    "K": 667,
    "L": 556,
    "M": 833,
    "N": 722,
    "O": 778,
    "P": 667,
    "Q": 778,
    "R": 722,
    "S": 667,
    "T": 611,
    "U": 722,
    "V": 667,
    "W": 944,
    "X": 667,
    "Y": 667,
    "Z": 611,
    "[": 278,
    "\\": 278,
    "]": 278,
    "^": 469,
    "_": 556,
    "`": 333,
    "a": 556,
    "b": 556,
    "c": 500,
    "d": 556,
    "e": 556,
    "f": 278,
    "g": 556,
    "h": 556,
    "i": 222,
    "j": 222,
    "k": 500,
    "l": 222,
    "m": 833,
    "n": 556,
    "o": 556,
    "p": 556,
    "q": 556,
    "r": 333,
    "s": 500,
    "t": 278,
    "u": 556,
    "v": 500,
    "w": 722,
    "x": 500,
    "y": 500,
    "z": 500,
    "{": 334,
    "|": 260,
    "}": 334,
    "~": 584,
}
_LARGURA_OMISSA = 600

_RE_INDIRECT = re.compile(rb"(\d+)\s+(\d+)\s+R")
_RE_OBJ = re.compile(rb"(\d+)\s+(\d+)\s+obj\b")
_RE_STREAM = re.compile(rb"stream\r?\n")
_RE_ENDSTREAM = re.compile(rb"endstream\b")
_RE_STRING = re.compile(rb"\((?:\\.|[^\\()])*\)")
_RE_NAME = re.compile(rb"/[^\s/\[\]()<>]+")
_RE_NUMBER = re.compile(rb"[+-]?(?:\d+\.\d*|\.\d+|\d+)")


@dataclass(frozen=True)
class ResultadoPdf:
    """Resultado da extracção PDF (sem OCR)."""

    paginas: list[PaginaExtraida]
    precisa_ocr: bool

    @property
    def texto(self) -> str:
        return "\n".join(p.texto for p in self.paginas if p.texto)


def _largura_texto(texto: str, tamanho: float) -> float:
    total = 0
    for ch in texto:
        total += _LARGURA_HELVETICA.get(ch, _LARGURA_OMISSA)
    return (total / 1000.0) * tamanho


def _desescapar_literal(bruto: bytes) -> str:
    # Literais PDF simples (sem octais complexos além do habitual).
    texto = bruto.decode("latin-1")
    saida: list[str] = []
    i = 0
    while i < len(texto):
        if texto[i] == "\\" and i + 1 < len(texto):
            seguinte = texto[i + 1]
            mapa = {"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f"}
            if seguinte in mapa:
                saida.append(mapa[seguinte])
                i += 2
            elif seguinte in "\\()":
                saida.append(seguinte)
                i += 2
            elif seguinte.isdigit():
                j = i + 1
                while j < len(texto) and j < i + 4 and texto[j].isdigit():
                    j += 1
                saida.append(chr(int(texto[i + 1 : j], 8) & 0xFF))
                i = j
            else:
                saida.append(seguinte)
                i += 2
        else:
            saida.append(texto[i])
            i += 1
    return "".join(saida)


def _carregar_objectos(dados: bytes) -> dict[int, bytes]:
    objectos: dict[int, bytes] = {}
    for match in _RE_OBJ.finditer(dados):
        numero = int(match.group(1))
        inicio = match.end()
        fim = dados.find(b"endobj", inicio)
        if fim < 0:
            continue
        objectos[numero] = dados[inicio:fim].strip()
    return objectos


def _corpo_stream(objecto: bytes) -> bytes | None:
    match = _RE_STREAM.search(objecto)
    if match is None:
        return None
    fim = _RE_ENDSTREAM.search(objecto, match.end())
    if fim is None:
        return None
    return objecto[match.end() : fim.start()]


def _dicionario_ate(objecto: bytes) -> bytes:
    stream = _RE_STREAM.search(objecto)
    if stream is not None:
        return objecto[: stream.start()]
    return objecto


def _refs(dicionario: bytes, chave: bytes) -> list[int]:
    padrao = re.compile(re.escape(chave) + rb"\s+(\d+)\s+(\d+)\s+R")
    encontrado = padrao.search(dicionario)
    if encontrado:
        return [int(encontrado.group(1))]
    padrao_arr = re.compile(
        re.escape(chave) + rb"\s*\[(.*?)\]", re.DOTALL
    )
    arr = padrao_arr.search(dicionario)
    if not arr:
        return []
    return [int(m.group(1)) for m in _RE_INDIRECT.finditer(arr.group(1))]


def _resolver_conteudos(
    objectos: dict[int, bytes], pagina_dict: bytes
) -> bytes:
    ids = _refs(pagina_dict, b"/Contents")
    if not ids:
        return b""
    partes: list[bytes] = []
    for oid in ids:
        obj = objectos.get(oid)
        if obj is None:
            continue
        # Contents pode ser um array de streams via objecto array.
        if obj.lstrip().startswith(b"["):
            for m in _RE_INDIRECT.finditer(obj):
                filho = objectos.get(int(m.group(1)))
                if filho is None:
                    continue
                fluxo = _corpo_stream(filho)
                if fluxo is not None:
                    partes.append(fluxo)
            continue
        fluxo = _corpo_stream(obj)
        if fluxo is not None:
            partes.append(fluxo)
    return b"\n".join(partes)


def _paginas_raiz(objectos: dict[int, bytes]) -> list[int]:
    catalogo = objectos.get(1)
    if catalogo is None:
        # Procurar /Catalog
        for obj in objectos.values():
            if b"/Type /Catalog" in obj or b"/Type/Catalog" in obj:
                catalogo = obj
                break
    if catalogo is None:
        raise ValueError("PDF sem catálogo")
    pages_ids = _refs(_dicionario_ate(catalogo), b"/Pages")
    if not pages_ids:
        raise ValueError("PDF sem /Pages")
    return _folhas_pagina(objectos, pages_ids[0])


def _folhas_pagina(objectos: dict[int, bytes], pages_id: int) -> list[int]:
    obj = objectos.get(pages_id)
    if obj is None:
        return []
    dicionario = _dicionario_ate(obj)
    if b"/Type /Page" in dicionario or b"/Type/Page\n" in dicionario or (
        b"/Type/Page" in dicionario and b"/Kids" not in dicionario
    ):
        if b"/Kids" not in dicionario:
            return [pages_id]
    kids = _refs(dicionario, b"/Kids")
    if not kids:
        # Array inline
        arr = re.search(rb"/Kids\s*\[(.*?)\]", dicionario, re.DOTALL)
        if arr:
            kids = [int(m.group(1)) for m in _RE_INDIRECT.finditer(arr.group(1))]
    folhas: list[int] = []
    for kid in kids:
        filho = objectos.get(kid)
        if filho is None:
            continue
        dic = _dicionario_ate(filho)
        if b"/Kids" in dic:
            folhas.extend(_folhas_pagina(objectos, kid))
        else:
            folhas.append(kid)
    return folhas


def _tokens_conteudo(fluxo: bytes) -> list[bytes]:
    tokens: list[bytes] = []
    i = 0
    n = len(fluxo)
    while i < n:
        b = fluxo[i]
        if b in b" \t\r\n":
            i += 1
            continue
        if b == ord("("):
            m = _RE_STRING.match(fluxo, i)
            if m:
                tokens.append(m.group(0))
                i = m.end()
                continue
            # fallback: avançar até ) simples
            j = i + 1
            while j < n and fluxo[j] != ord(")"):
                if fluxo[j] == ord("\\"):
                    j += 2
                else:
                    j += 1
            tokens.append(fluxo[i : j + 1])
            i = j + 1
            continue
        if b == ord("/"):
            m = _RE_NAME.match(fluxo, i)
            if m:
                tokens.append(m.group(0))
                i = m.end()
                continue
        if b in b"[]":
            tokens.append(fluxo[i : i + 1])
            i += 1
            continue
        if fluxo.startswith(b"BI", i) or fluxo.startswith(b"ID", i) or fluxo.startswith(
            b"EI", i
        ):
            # Imagem inline: saltar até EI
            if fluxo.startswith(b"BI", i):
                fim = fluxo.find(b"EI", i + 2)
                if fim < 0:
                    break
                tokens.append(b"BI")
                i = fim + 2
                continue
        m = _RE_NUMBER.match(fluxo, i)
        if m and (i + 1 >= n or not (48 <= fluxo[i] <= 57 and False)):
            # número ou operador alfanumérico?
            pass
        # operador ou número
        if (48 <= b <= 57) or b in b"+-.":
            m = _RE_NUMBER.match(fluxo, i)
            if m:
                tokens.append(m.group(0))
                i = m.end()
                continue
        # palavra / operador
        j = i
        while j < n and fluxo[j] not in b" \t\r\n/[]()<>":
            j += 1
        if j == i:
            i += 1
            continue
        tokens.append(fluxo[i:j])
        i = j
    return tokens


def _extrair_spans_fluxo(fluxo: bytes, numero_pagina: int) -> list[SpanExtraido]:
    tokens = _tokens_conteudo(fluxo)
    spans: list[SpanExtraido] = []
    em_texto = False
    tamanho = 12.0
    tx = 0.0
    ty = 0.0
    offset = 0
    partes_texto: list[str] = []

    def emitir(texto: str) -> None:
        nonlocal offset, tx
        if not texto:
            return
        largura = _largura_texto(texto, tamanho)
        altura = tamanho
        # y no PDF é a linha de base; a caixa cobre a linha tipográfica.
        caixa = Caixa(
            pagina=numero_pagina,
            x=tx,
            y=ty,
            largura=max(largura, 0.1),
            altura=max(altura, 0.1),
        )
        spans.append(
            SpanExtraido(
                texto=texto,
                offset_inicio=offset,
                offset_fim=offset + len(texto),
                caixa=caixa,
            )
        )
        partes_texto.append(texto)
        offset += len(texto)
        tx += largura

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == b"BT":
            em_texto = True
            i += 1
            continue
        if tok == b"ET":
            em_texto = False
            i += 1
            continue
        if not em_texto:
            i += 1
            continue
        if tok == b"Tf" and i >= 2:
            try:
                tamanho = float(tokens[i - 1])
            except ValueError:
                pass
            i += 1
            continue
        if tok == b"Tm" and i >= 6:
            try:
                tx = float(tokens[i - 2])
                ty = float(tokens[i - 1])
            except ValueError:
                pass
            i += 1
            continue
        if tok == b"Td" and i >= 2:
            try:
                tx += float(tokens[i - 2])
                ty += float(tokens[i - 1])
            except ValueError:
                pass
            i += 1
            continue
        if tok == b"TD" and i >= 2:
            try:
                tx += float(tokens[i - 2])
                ty += float(tokens[i - 1])
            except ValueError:
                pass
            i += 1
            continue
        if tok == b"Tj" and i >= 1 and tokens[i - 1].startswith(b"("):
            emitir(_desescapar_literal(tokens[i - 1][1:-1]))
            i += 1
            continue
        if tok == b"'" and i >= 1 and tokens[i - 1].startswith(b"("):
            emitir(_desescapar_literal(tokens[i - 1][1:-1]))
            i += 1
            continue
        if tok == b"TJ" and i >= 1 and tokens[i - 1] == b"]":
            # Percorrer o array imediatamente anterior.
            j = i - 1
            profundidade = 0
            inicio_arr = j
            while j >= 0:
                if tokens[j] == b"]":
                    profundidade += 1
                elif tokens[j] == b"[":
                    profundidade -= 1
                    if profundidade == 0:
                        inicio_arr = j
                        break
                j -= 1
            pedacos: list[str] = []
            for t in tokens[inicio_arr + 1 : i - 1]:
                if t.startswith(b"("):
                    pedacos.append(_desescapar_literal(t[1:-1]))
            if pedacos:
                emitir("".join(pedacos))
            i += 1
            continue
        i += 1

    # Ajustar offsets: o texto da página é a concatenação dos spans com
    # espaços entre spans consecutivos quando não há pontuação de junção.
    if not spans:
        return []
    texto_pagina_partes: list[str] = []
    spans_ajustados: list[SpanExtraido] = []
    cursor = 0
    for indice, span in enumerate(spans):
        if indice > 0:
            texto_pagina_partes.append(" ")
            cursor += 1
        texto_pagina_partes.append(span.texto)
        spans_ajustados.append(
            SpanExtraido(
                texto=span.texto,
                offset_inicio=cursor,
                offset_fim=cursor + len(span.texto),
                caixa=span.caixa,
            )
        )
        cursor += len(span.texto)
    return spans_ajustados


def _texto_de_spans(spans: list[SpanExtraido]) -> str:
    if not spans:
        return ""
    partes: list[str] = []
    for indice, span in enumerate(spans):
        if indice > 0:
            partes.append(" ")
        partes.append(span.texto)
    return "".join(partes)


def extrair_pdf(caminho: Path | str) -> ResultadoPdf:
    """Extrai páginas com texto e caixas; ``precisa_ocr`` se não houver texto."""
    destino = Path(caminho)
    if not destino.is_file():
        raise FicheiroInexistente(str(destino))

    dados = destino.read_bytes()
    if not dados.startswith(b"%PDF"):
        raise ValueError(f"não é um PDF: {destino}")

    objectos = _carregar_objectos(dados)
    ids_paginas = _paginas_raiz(objectos)
    paginas: list[PaginaExtraida] = []
    for indice, page_id in enumerate(ids_paginas, start=1):
        pagina_obj = objectos[page_id]
        dicionario = _dicionario_ate(pagina_obj)
        fluxo = _resolver_conteudos(objectos, dicionario)
        spans = _extrair_spans_fluxo(fluxo, indice)
        texto = _texto_de_spans(spans)
        paginas.append(PaginaExtraida(numero=indice, texto=texto, spans=spans))

    tem_texto = any(p.texto.strip() for p in paginas)
    precisa_ocr = not tem_texto
    return ResultadoPdf(paginas=paginas, precisa_ocr=precisa_ocr)


__all__ = ["ResultadoPdf", "extrair_pdf"]
