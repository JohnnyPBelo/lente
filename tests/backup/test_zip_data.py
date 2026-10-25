"""Regressão REG-BAK-001, REG-BAK-002 e REG-SEG-005: cópia zip local."""

from __future__ import annotations

import ast
import inspect
import zipfile
from pathlib import Path

import pytest


@pytest.fixture
def pasta_data(tmp_path: Path) -> Path:
    pasta = tmp_path / "data"
    pasta.mkdir(parents=True, exist_ok=True)
    sqlite = pasta / "lente.sqlite"
    sqlite.write_bytes(b"SQLite formato sinteticamente curto\n" + b"\x00" * 64)
    (pasta / "miniaturas").mkdir()
    (pasta / "miniaturas" / "doc1.webp").write_bytes(b"WEBP-FAKE")
    return pasta


def test_reg_bak_001(pasta_data: Path, tmp_path: Path) -> None:
    """Zip contém o sqlite de fixture e extrai bit a bit igual."""
    from engine.backup.zip_data import criar_copia

    destino = tmp_path / "destino" / "lente-data.zip"
    criado = criar_copia(pasta_data, destino)
    assert criado == destino
    assert destino.is_file()

    with zipfile.ZipFile(destino, "r") as zf:
        nomes = set(zf.namelist())
        assert any(n.endswith("lente.sqlite") or n == "lente.sqlite" for n in nomes)
        # Encontrar a entrada do sqlite.
        entrada_sqlite = next(
            n for n in nomes if n.rstrip("/").endswith("lente.sqlite")
        )
        extraido = zf.read(entrada_sqlite)

    original = (pasta_data / "lente.sqlite").read_bytes()
    assert extraido == original


def test_reg_bak_002(pasta_data: Path, tmp_path: Path) -> None:
    """Destino é caminho local; o módulo não faz upload."""
    from engine.backup import zip_data

    destino = tmp_path / "copia-local.zip"
    caminho = zip_data.criar_copia(pasta_data, destino)
    assert Path(caminho).is_absolute() or Path(caminho).exists()
    assert Path(caminho).resolve().is_relative_to(tmp_path.resolve()) or Path(
        caminho
    ).exists()
    assert Path(caminho).is_file()

    for nome in ("upload", "enviar_nuvem", "s3", "put_object", "sync_remoto"):
        assert not hasattr(zip_data, nome)

    fonte = inspect.getsource(zip_data)
    arvore = ast.parse(fonte)
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for alias in no.names:
                raiz = alias.name.split(".")[0]
                assert raiz not in {
                    "urllib",
                    "urllib3",
                    "requests",
                    "httpx",
                    "aiohttp",
                    "boto3",
                    "botocore",
                    "ftplib",
                }
        if isinstance(no, ast.ImportFrom) and no.module:
            raiz = no.module.split(".")[0]
            assert raiz not in {
                "urllib",
                "urllib3",
                "requests",
                "httpx",
                "aiohttp",
                "boto3",
                "botocore",
                "ftplib",
                "http",
            }


def test_reg_seg_005() -> None:
    """Diário, SQLite e backup não abrem cliente HTTP de upload."""
    import engine.backup.zip_data as zip_data
    import engine.diario.escrever as escrever
    import engine.diario.ler as ler

    clientes = {
        "Client",
        "Session",
        "urlopen",
        "put",
        "post",
        "upload_file",
        "upload_fileobj",
    }
    for modulo in (escrever, ler, zip_data):
        fonte = inspect.getsource(modulo)
        arvore = ast.parse(fonte)
        nomes_importados: set[str] = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                for alias in no.names:
                    nomes_importados.add(alias.name.split(".")[0])
                    if alias.asname:
                        nomes_importados.add(alias.asname)
            if isinstance(no, ast.ImportFrom) and no.module:
                nomes_importados.add(no.module.split(".")[0])
                for alias in no.names:
                    nomes_importados.add(alias.name)
                    if alias.asname:
                        nomes_importados.add(alias.asname)
        assert not nomes_importados & {
            "urllib",
            "urllib3",
            "requests",
            "httpx",
            "aiohttp",
            "boto3",
            "http",
        }
        # Sem construção óbvia de cliente de upload no corpo.
        for no in ast.walk(arvore):
            if isinstance(no, ast.Call):
                func = no.func
                if isinstance(func, ast.Attribute) and func.attr in clientes:
                    # zipfile / sqlite3 / pathlib são locais — só falha se for HTTP
                    alvo = ""
                    if isinstance(func.value, ast.Name):
                        alvo = func.value.id
                    assert alvo not in {
                        "requests",
                        "httpx",
                        "urllib",
                        "client",
                        "s3",
                        "session",
                    }, f"chamada de upload em {modulo.__name__}: {alvo}.{func.attr}"
