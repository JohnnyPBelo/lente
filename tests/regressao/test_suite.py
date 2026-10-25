"""Regressões que já correm, antes de existir motor ou interface."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import apoio

REQ_NO_TEXTO = re.compile(r"REQ-[A-Z]+[0-9]*-\d+")


def test_manifesto_sem_duplicados() -> None:
    linhas = apoio.ler_manifesto()
    assert linhas, "O manifesto tem de listar os testes que já correm."
    repetidos = apoio.duplicados(linhas)
    assert not repetidos, f"Linhas repetidas no manifesto: {repetidos}"


def test_manifesto_nao_encolhe() -> None:
    problemas = apoio.encolhimentos()
    assert not problemas, "\n".join(problemas)


def test_manifesto_ids_recolhidos() -> None:
    em_falta = apoio.ids_em_falta()
    assert not em_falta, "\n".join(em_falta)


def test_esquemas_json_aceitam_exemplos() -> None:
    apoio.validar_exemplos()


def test_cada_req_aparece_uma_vez_na_cobertura() -> None:
    requisitos = apoio.requisitos_dos_ficheiros()
    assert len(requisitos) == len(set(requisitos)), "Há um REQ repetido nos ficheiros."
    texto = (apoio.raiz() / apoio.COBERTURA_REL).read_text(encoding="utf-8")
    mencionados = REQ_NO_TEXTO.findall(texto)
    contagem: dict[str, int] = {}
    for identificador in mencionados:
        contagem[identificador] = contagem.get(identificador, 0) + 1
    em_falta = [req for req in requisitos if contagem.get(req, 0) == 0]
    a_mais = sorted(set(contagem) - set(requisitos))
    repetidos = sorted(req for req, n in contagem.items() if n != 1)
    assert not em_falta, f"REQ em falta na cobertura: {em_falta}"
    assert not a_mais, f"A cobertura cita REQ que não existem: {a_mais}"
    assert not repetidos, f"Cada REQ tem de aparecer uma só vez: {repetidos}"

    linhas = apoio.linhas_de_cobertura()
    assert {req for req, *_resto in linhas} == set(requisitos)
    assert len(linhas) == len(requisitos)
    for req, reg, pln, _estado in linhas:
        assert reg == "REG" + req[3:], f"{req} devia mapear para REG{req[3:]}, não {reg}."
        numero = int(pln.removeprefix("PLN-"))
        assert 1 <= numero <= 21, f"{req} aponta para um plano fora de PLN-01..21."
    declarada = apoio.contagem_declarada()
    assert declarada == len(requisitos), (
        f"A cobertura declara {declarada} linhas e os ficheiros têm {len(requisitos)} requisitos."
    )


def test_reg_agora_estao_no_manifesto() -> None:
    faltam = apoio.reg_agora_em_falta()
    assert not faltam, f"Marcados como agora e ausentes do manifesto: {faltam}"


def test_nao_ha_pesos_de_modelo_versionados() -> None:
    pesos = apoio.pesos_versionados()
    assert not pesos, f"Pesos de modelo não entram no git: {pesos}"


def test_plano_origem_e_buracos() -> None:
    apoio.plano_e_buracos()


def test_reg_fbk_001() -> None:
    """REG-FBK-001: copy das acções Acertou / Corrigir / Descartar existe."""
    texto = (apoio.raiz() / "docs" / "interface" / "copy.md").read_text(encoding="utf-8")
    for chave in ("feedback.hit", "feedback.fix", "feedback.dismiss"):
        assert chave in texto, f"Falta {chave} em copy.md"
    assert "Acertou" in texto and "Corrigir" in texto and "Descartar" in texto


def test_reg_fbk_003() -> None:
    """REG-FBK-003: link discreto para corrigir mais tarde na copy."""
    texto = (apoio.raiz() / "docs" / "interface" / "copy.md").read_text(encoding="utf-8")
    assert "feedback.fix_later" in texto
    assert "Corrigir mais tarde" in texto


def test_cobertura_toda_agora() -> None:
    """Cada REQ tem linha agora e o REG correspondente está no manifesto."""
    requisitos = apoio.requisitos_dos_ficheiros()
    linhas = apoio.linhas_de_cobertura()
    assert len(linhas) == len(requisitos)
    assert {req for req, *_ in linhas} == set(requisitos)
    manifesto = apoio.ler_manifesto()
    pendentes = []
    sem_reg = []
    for req, reg, _pln, estado in linhas:
        if estado != "agora":
            pendentes.append(f"{req}={estado}")
        if not apoio.manifesto_cobre_reg(reg, manifesto):
            sem_reg.append(reg)
    assert not pendentes, f"Linhas ainda pendentes: {pendentes}"
    assert not sem_reg, f"REG ausentes do manifesto: {sem_reg}"
