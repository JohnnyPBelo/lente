"""Apoio da suite de regressão. Sem dependências fora da biblioteca padrão."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ_MARCADOR = "docs/origem/plano.md"
MANIFESTO_REL = "tests/regressao/manifesto.txt"
COBERTURA_REL = "docs/verificacao/cobertura.md"
MATRIZ_REL = "docs/rastreio/matriz.md"
PESOS = {".gguf", ".onnx", ".safetensors", ".pt", ".pth"}
REQ_RE = re.compile(r"^## (REQ-[A-Z]+[0-9]*-\d+)\s*$", re.MULTILINE)
LINHA_COBERTURA = re.compile(
    r"^\|\s*(REQ-[A-Z]+[0-9]*-\d+)\s*\|\s*(REG-[A-Z]+[0-9]*-\d+)\s*\|\s*(PLN-\d+)\s*\|\s*(agora|pendente)\s*\|",
    re.MULTILINE,
)
CONTAGEM_RE = re.compile(r"A tabela tem (\d+) linhas, uma por requisito\.")
BURACOS = (
    "Nenhum. Todas as secções `##` de [docs/origem/plano.md](../origem/plano.md) "
    "e a introdução sem `##` têm destino na tabela principal "
    "(REQ e/ou ADR e/ou PLN e docs relacionados). "
    "A secção «De fora…» mapeia para `REQ-FOR-*` e `ADR-016` (exclusões), "
    "sem plano de implementação do comportamento excluído."
)
DATA_HORA = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


def raiz() -> Path:
    aqui = Path(__file__).resolve()
    for candidato in [aqui, *aqui.parents]:
        if (candidato / RAIZ_MARCADOR).is_file() and (candidato / ".git").exists():
            return candidato
    raise RuntimeError("Não encontrei a raiz do repositório Lente.")


def ler_manifesto(caminho: Path | None = None) -> list[str]:
    destino = caminho or (raiz() / MANIFESTO_REL)
    texto = destino.read_text(encoding="utf-8")
    linhas = []
    for bruta in texto.splitlines():
        linha = bruta.strip()
        if not linha:
            continue
        if linha.startswith("#"):
            raise AssertionError(
                f"O manifesto não aceita comentários (linha {linha!r}). "
                "Cada linha é um node id do pytest ou um caminho Vitest."
            )
        linhas.append(linha)
    return linhas


def duplicados(linhas: list[str]) -> list[str]:
    vistos: set[str] = set()
    repetidos: list[str] = []
    for linha in linhas:
        if linha in vistos and linha not in repetidos:
            repetidos.append(linha)
        vistos.add(linha)
    return repetidos


def _git(args: list[str], verificar: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=raiz(),
        check=verificar,
        capture_output=True,
        text=True,
    )


def _rev(ref: str) -> str | None:
    proc = _git(["rev-parse", "--verify", "--quiet", ref])
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def manifesto_no_commit(rev: str) -> list[str]:
    if _rev(rev) is None:
        raise AssertionError(f"A revisão {rev} não existe neste clone.")
    alvo = f"{rev}:{MANIFESTO_REL}"
    existe = _git(["cat-file", "-e", alvo])
    if existe.returncode != 0:
        return []
    proc = _git(["show", alvo])
    if proc.returncode != 0:
        raise AssertionError(proc.stderr.strip() or f"Não li {alvo}.")
    linhas = []
    for bruta in proc.stdout.splitlines():
        linha = bruta.strip()
        if linha:
            linhas.append(linha)
    return linhas


def revisoes_de_base() -> list[str]:
    """Commits cujo manifesto tem de ser prefixo do actual.

    No GitHub Actions usa-se REGRESSAO_BASE_SHA (base do pull request ou
    commit anterior no push). Localmente compara-se com o ficheiro já
    commitado e, se existir, com origin/main ou com o pai de main.
    """
    explicita = os.environ.get("REGRESSAO_BASE_SHA", "").strip()
    if explicita:
        if set(explicita) == {"0"}:
            return []
        if _rev(explicita) is None:
            raise AssertionError(
                f"REGRESSAO_BASE_SHA={explicita} não está neste clone. "
                "O workflow tem de obter esse commit antes da suite."
            )
        return [explicita]

    revisoes: list[str] = []
    if _rev("HEAD") is not None:
        revisoes.append("HEAD")
    origem = _rev("origin/main")
    cabeca = _rev("HEAD")
    if origem and cabeca and origem != cabeca:
        revisoes.append("origin/main")
    elif origem and cabeca and origem == cabeca and _rev("HEAD~1"):
        revisoes.append("HEAD~1")
    elif origem is None and _rev("HEAD~1"):
        revisoes.append("HEAD~1")
    return revisoes


def _unicos_na_ordem(linhas: list[str]) -> list[str]:
    """Primeira ocorrência de cada linha, na ordem do manifesto."""
    vistos: set[str] = set()
    saida: list[str] = []
    for linha in linhas:
        if linha in vistos:
            continue
        vistos.add(linha)
        saida.append(linha)
    return saida


def encolhimentos() -> list[str]:
    """O manifesto só cresce; remover uma repetição exacta de uma linha já listada é permitido."""
    actual = _unicos_na_ordem(ler_manifesto())
    problemas: list[str] = []
    for rev in revisoes_de_base():
        base = _unicos_na_ordem(manifesto_no_commit(rev))
        if actual[: len(base)] != base:
            problemas.append(
                f"O manifesto encolheu ou reordenou linhas face a {rev}. "
                "Só se acrescentam linhas no fim "
                "(repetições exactas de uma linha já presente podem sair)."
            )
    return problemas


def _funcao_existe(nodeid: str) -> None:
    ficheiro, separador, resto = nodeid.partition("::")
    if not separador or not resto or "[" in resto or "::" in resto:
        raise AssertionError(
            f"Node id inválido {nodeid!r}. Use caminho::nome_da_funcao, sem parâmetros."
        )
    caminho = raiz() / ficheiro
    if not caminho.is_file():
        raise AssertionError(f"Não existe o ficheiro do teste {ficheiro}.")
    nome_mod = "lente_regressao_" + re.sub(r"[^0-9a-zA-Z_]", "_", ficheiro)
    spec = importlib.util.spec_from_file_location(nome_mod, caminho)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Não consegui importar {ficheiro}.")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    funcao = getattr(modulo, resto, None)
    if not callable(funcao):
        raise AssertionError(f"{nodeid} não é uma função neste módulo.")


def nodeids_recolhidos() -> set[str]:
    """Recolhe node ids dos ficheiros pytest listados no manifesto.

    O manifesto cresce com testes em ``tests/<pacote>/``, não só em
    ``tests/regressao/``; a recolha segue esses caminhos.
    """
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    ficheiros = sorted(
        {
            linha.partition("::")[0]
            for linha in ler_manifesto()
            if "::" in linha
        }
    )
    if not ficheiros:
        return set()
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            "-p",
            "no:cacheprovider",
            *ficheiros,
        ],
        cwd=raiz(),
        capture_output=True,
        text=True,
        env=env,
    )
    if proc.returncode != 0:
        detalhe = (proc.stdout + "\n" + proc.stderr).strip()
        raise AssertionError(f"A recolha do pytest falhou.\n{detalhe}")
    ids: set[str] = set()
    for linha in proc.stdout.splitlines():
        linha = linha.strip()
        if "::" in linha and not linha.startswith("="):
            ids.add(linha.split()[0])
    return ids


def ids_em_falta(linhas: list[str] | None = None) -> list[str]:
    linhas = ler_manifesto() if linhas is None else linhas
    em_falta: list[str] = []
    pytest_ids = [linha for linha in linhas if "::" in linha]
    vitest = [linha for linha in linhas if "::" not in linha]
    for nodeid in pytest_ids:
        try:
            _funcao_existe(nodeid)
        except AssertionError as erro:
            em_falta.append(str(erro))
    recolhidos = nodeids_recolhidos() if pytest_ids else set()
    for nodeid in pytest_ids:
        if nodeid not in recolhidos:
            em_falta.append(f"O pytest não recolheu {nodeid}.")
    ui = raiz() / "apps" / "ui"
    for caminho in vitest:
        if not ui.is_dir():
            em_falta.append(
                f"O manifesto lista o teste de UI {caminho}, mas apps/ui ainda não existe."
            )
            continue
        if not (raiz() / caminho).is_file():
            em_falta.append(f"Não existe o teste de UI {caminho}.")
    return em_falta


def requisitos_dos_ficheiros() -> list[str]:
    pasta = raiz() / "docs" / "requisitos"
    encontrados: list[str] = []
    for caminho in sorted(pasta.glob("*.md")):
        if caminho.name == "README.md":
            continue
        encontrados.extend(REQ_RE.findall(caminho.read_text(encoding="utf-8")))
    return encontrados


def linhas_de_cobertura() -> list[tuple[str, str, str, str]]:
    texto = (raiz() / COBERTURA_REL).read_text(encoding="utf-8")
    return [tuple(m.groups()) for m in LINHA_COBERTURA.finditer(texto)]  # type: ignore[misc]


def contagem_declarada() -> int | None:
    texto = (raiz() / COBERTURA_REL).read_text(encoding="utf-8")
    achado = CONTAGEM_RE.search(texto)
    if not achado:
        return None
    return int(achado.group(1))


def reg_normalizado(reg: str) -> str:
    return reg.removeprefix("REG-").lower().replace("-", "_")


def manifesto_cobre_reg(reg: str, linhas: list[str]) -> bool:
    """REG-ING-001 casa com test_reg_ing_001 ou com reg-ing-001 no caminho."""
    chave = "reg_" + reg_normalizado(reg)
    for linha in linhas:
        if chave in linha.lower().replace("-", "_"):
            return True
    return False


def reg_agora_em_falta() -> list[str]:
    linhas = ler_manifesto()
    faltam = []
    for req, reg, _pln, estado in linhas_de_cobertura():
        if estado != "agora":
            continue
        if not manifesto_cobre_reg(reg, linhas):
            faltam.append(f"{reg} ({req})")
    return faltam


def _tipo_ok(valor: object, tipo: str) -> bool:
    if tipo == "object":
        return isinstance(valor, dict)
    if tipo == "array":
        return isinstance(valor, list)
    if tipo == "string":
        return isinstance(valor, str)
    if tipo == "integer":
        return isinstance(valor, int) and not isinstance(valor, bool)
    if tipo == "number":
        return isinstance(valor, (int, float)) and not isinstance(valor, bool)
    if tipo == "boolean":
        return isinstance(valor, bool)
    if tipo == "null":
        return valor is None
    raise AssertionError(f"Tipo de esquema não suportado por este verificador: {tipo}.")


def validar_instancia(valor: object, esquema: dict, caminho: str = "$") -> None:
    """Subconjunto documentado de JSON Schema: required, type, const, enum,
    additionalProperties, properties, items, pattern, minLength, minimum,
    minItems e format date-time. Não é um validador JSON Schema completo.
    """
    if "const" in esquema and valor != esquema["const"]:
        raise AssertionError(f"{caminho} devia ser {esquema['const']!r}.")
    if "enum" in esquema and valor not in esquema["enum"]:
        raise AssertionError(f"{caminho} não está no enum {esquema['enum']!r}.")
    tipos = esquema.get("type")
    if isinstance(tipos, str):
        tipos = [tipos]
    if tipos and not any(_tipo_ok(valor, tipo) for tipo in tipos):
        raise AssertionError(f"{caminho} não cumpre o tipo {tipos!r}.")
    if isinstance(valor, str):
        if "minLength" in esquema and len(valor) < esquema["minLength"]:
            raise AssertionError(f"{caminho} é mais curto do que minLength.")
        if "pattern" in esquema and re.fullmatch(esquema["pattern"], valor) is None:
            raise AssertionError(f"{caminho} não cumpre o padrão.")
        if esquema.get("format") == "date-time" and DATA_HORA.fullmatch(valor) is None:
            raise AssertionError(f"{caminho} não é uma data-hora ISO-8601 aceite.")
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        if "minimum" in esquema and valor < esquema["minimum"]:
            raise AssertionError(f"{caminho} é inferior ao mínimo.")
    if isinstance(valor, dict):
        for chave in esquema.get("required", []):
            if chave not in valor:
                raise AssertionError(f"{caminho} não tem a chave obrigatória {chave}.")
        propriedades = esquema.get("properties", {})
        extra = esquema.get("additionalProperties", True)
        for chave, filho in valor.items():
            if chave in propriedades:
                validar_instancia(filho, propriedades[chave], f"{caminho}.{chave}")
            elif extra is False:
                raise AssertionError(f"{caminho} tem a chave não prevista {chave}.")
            elif isinstance(extra, dict):
                validar_instancia(filho, extra, f"{caminho}.{chave}")
    if isinstance(valor, list):
        if "minItems" in esquema and len(valor) < esquema["minItems"]:
            raise AssertionError(f"{caminho} tem menos itens do que minItems.")
        item = esquema.get("items")
        if isinstance(item, dict):
            for indice, filho in enumerate(valor):
                validar_instancia(filho, item, f"{caminho}[{indice}]")


def pares_exemplo_esquema() -> list[tuple[Path, Path]]:
    pasta = raiz() / "docs" / "dados" / "exemplos"
    pares: list[tuple[Path, Path]] = []
    for exemplo in sorted(pasta.glob("*.json")):
        nome = exemplo.name.replace(".exemplo.json", ".schema.json")
        esquema = raiz() / "docs" / "dados" / nome
        if not esquema.is_file():
            raise AssertionError(
                f"{exemplo.name} não tem esquema {nome} em docs/dados/."
            )
        pares.append((esquema, exemplo))
    if not pares:
        raise AssertionError("Não há exemplos JSON em docs/dados/exemplos/.")
    return pares


def validar_exemplos() -> None:
    for esquema_path, exemplo_path in pares_exemplo_esquema():
        esquema = json.loads(esquema_path.read_text(encoding="utf-8"))
        exemplo = json.loads(exemplo_path.read_text(encoding="utf-8"))
        validar_instancia(exemplo, esquema, exemplo_path.name)


def pesos_versionados() -> list[str]:
    proc = _git(["ls-files", "-z"])
    if proc.returncode != 0:
        raise AssertionError(proc.stderr.strip() or "git ls-files falhou.")
    achados = []
    for nome in proc.stdout.split("\0"):
        if not nome:
            continue
        sufixo = Path(nome).suffix.lower()
        if sufixo in PESOS:
            achados.append(nome)
    return achados


def plano_e_buracos() -> None:
    plano = raiz() / RAIZ_MARCADOR
    if not plano.is_file():
        raise AssertionError("docs/origem/plano.md tem de continuar no repositório.")
    matriz = (raiz() / MATRIZ_REL).read_text(encoding="utf-8")
    if "## Buracos" not in matriz:
        raise AssertionError("docs/rastreio/matriz.md tem de ter a secção Buracos.")
    seccao = matriz.split("## Buracos", 1)[1]
    seccao = seccao.split("\n## ", 1)[0]
    if BURACOS not in seccao:
        raise AssertionError(
            "A secção Buracos já não diz que não há buracos, com a redacção actual."
        )
