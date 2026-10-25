"""Motor de migrações versionadas via ``PRAGMA user_version``."""

from __future__ import annotations

import re
from pathlib import Path

from engine.armazenamento.ligacao import abrir_ligacao

PASTA_ESQUEMA = Path(__file__).resolve().parent / "esquema"
PADRAO_FICHEIRO = re.compile(r"^(\d{3})_.+\.sql$")


def listar_migracoes(pasta: Path | None = None) -> list[tuple[int, Path]]:
    """Lista ficheiros ``NNN_….sql`` ordenados pelo número de versão."""
    origem = pasta or PASTA_ESQUEMA
    encontrados: list[tuple[int, Path]] = []
    for ficheiro in origem.iterdir():
        if not ficheiro.is_file():
            continue
        correspondencia = PADRAO_FICHEIRO.match(ficheiro.name)
        if correspondencia is None:
            continue
        encontrados.append((int(correspondencia.group(1)), ficheiro))
    encontrados.sort(key=lambda item: item[0])
    return encontrados


def aplicar_migracoes(caminho: Path | str, pasta: Path | None = None) -> int:
    """Aplica migrações pendentes em ordem; idempotente se já aplicadas.

    Devolve o ``user_version`` final.
    """
    destino = Path(caminho)
    migracoes = listar_migracoes(pasta)
    with abrir_ligacao(destino) as ligacao:
        actual = int(ligacao.execute("PRAGMA user_version").fetchone()[0])
        for versao, ficheiro in migracoes:
            if versao <= actual:
                continue
            sql = ficheiro.read_text(encoding="utf-8")
            # executescript faz COMMIT no início; em seguida fixamos user_version.
            ligacao.executescript(sql)
            ligacao.execute(f"PRAGMA user_version = {int(versao)}")
            actual = versao
        return actual
