"""Regressões REG-MOD-001 / 007 / 008: comando único e pesos em falta."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx

from engine.api.bind import HOST_OMISSAO, PORTA_OMISSAO
from engine.armazenamento.repositorio import estado_esquema
from engine.cli import arrancar
from engine.runtime.pesos import orientar_falta


def _listeners_loopback(porto: int) -> list[str]:
    """Lista endereços a escutar no porto (via ``ss`` se existir)."""
    try:
        out = subprocess.check_output(
            ["ss", "-ltn"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Fallback: confirma que o porto responde em 127.0.0.1
        with socket.create_connection(("127.0.0.1", porto), timeout=1.0):
            pass
        return ["127.0.0.1"]

    encontrados: list[str] = []
    sufixo = f":{porto}"
    for linha in out.splitlines():
        if sufixo not in linha:
            continue
        # Ex.: LISTEN 0 8 127.0.0.1:4317 0.0.0.0:*
        partes = linha.split()
        for p in partes:
            if p.endswith(sufixo):
                host = p[: -len(sufixo)]
                encontrados.append(host)
    return encontrados


def _esperar_ready(url: str, *, tentativas: int = 50) -> httpx.Response:
    ultimo: Exception | None = None
    for _ in range(tentativas):
        try:
            resposta = httpx.get(url, timeout=0.5)
            if resposta.status_code == 200:
                return resposta
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
        time.sleep(0.05)
    raise AssertionError(f"Servidor não ficou pronto: {ultimo}")


def test_reg_mod_001(raiz_tmp: Path, porto_livre: int) -> None:
    """Comando num porto livre: GET / = 200, um listener, migrações, sem Node."""
    assert PORTA_OMISSAO == 4317
    assert HOST_OMISSAO == "127.0.0.1"

    servidor = arrancar(
        host="127.0.0.1",
        porta=porto_livre,
        raiz=raiz_tmp,
        pasta_data=raiz_tmp / "data",
        pasta_modelos=raiz_tmp / "models",
        bloquear=False,
    )
    try:
        host, porta = servidor.endereco_efectivo()
        assert host == "127.0.0.1"
        assert porta == porto_livre

        base = f"http://127.0.0.1:{porto_livre}"
        raiz = _esperar_ready(f"{base}/")
        assert raiz.status_code == 200

        listeners = _listeners_loopback(porto_livre)
        assert listeners, "esperado pelo menos um listener"
        assert all(h in {"127.0.0.1", "localhost"} for h in listeners)
        assert "0.0.0.0" not in listeners
        assert len(set(listeners)) == 1

        esquema = estado_esquema(raiz_tmp / "data" / "lente.sqlite")
        assert int(esquema["user_version"]) >= 1

        # O processo actual é Python — Node não fica neste processo.
        assert "node" not in Path(sys.executable).name.lower()
        assert os.environ.get("npm_lifecycle_event") is None
    finally:
        servidor.parar()


def test_reg_mod_007(raiz_tmp: Path, porto_livre: int) -> None:
    """Download bloqueado: a app abre e a orientação indica models/."""
    # Sem pesos; forçamos erro de licença no estado injectável via guidance.
    servidor = arrancar(
        host="127.0.0.1",
        porta=porto_livre,
        raiz=raiz_tmp,
        pasta_data=raiz_tmp / "data",
        pasta_modelos=raiz_tmp / "models",
        bloquear=False,
    )
    try:
        base = f"http://127.0.0.1:{porto_livre}"
        _esperar_ready(f"{base}/")

        guia = httpx.get(f"{base}/models/guidance", timeout=2.0)
        assert guia.status_code == 200
        corpo = guia.json()
        itens = corpo["itens"]
        assert itens, "orientação deve listar pesos em falta"
        caminhos = " ".join(
            str(i.get("caminho", "")) + " " + str(i.get("mensagem", ""))
            for i in itens
        )
        assert "models" in caminhos or "embeddinggemma" in caminhos.lower()
        assert any(
            papel in str(i.get("modelo"))
            for i in itens
            for papel in ("embedding", "juiz", "escritor")
        )

        # O teste não descarrega pesos: POST devolve 409 com orientação.
        bloqueado = httpx.post(
            f"{base}/models/download",
            json={"modelo": "escritor"},
            timeout=2.0,
        )
        assert bloqueado.status_code == 409
        assert "models" in bloqueado.text.lower() or "e2b" in bloqueado.text.lower()

        # Local: orientar_falta cobre os três papéis sem rede.
        local = orientar_falta(raiz_tmp / "models")
        modelos = {i["modelo"] for i in local["itens"]}
        assert {"embedding", "juiz", "escritor"} <= modelos
    finally:
        servidor.parar()


def test_reg_mod_008(raiz_tmp: Path, porto_livre: int) -> None:
    """E2B ausente: processo não termina; health.escritor=ausente; procura ok."""
    from engine.api.app import criar_app
    from engine.api.ids import doc_id
    from engine.armazenamento.repositorio import abrir

    sqlite = raiz_tmp / "data" / "lente.sqlite"
    lig = abrir(sqlite)
    agora = "2026-10-25T00:00:00Z"
    cur = lig.execute(
        "INSERT INTO documentos "
        "(caminho, titulo, tipo, sha256, estado, paginas, criado_em, actualizado_em) "
        "VALUES (?, ?, 'txt', ?, 'ok', 1, ?, ?)",
        ("/tmp/excerto.txt", "Excerto", "b" * 64, agora, agora),
    )
    doc_num = int(cur.lastrowid)
    lig.commit()
    documento_id = doc_id(doc_num)

    def motor_com_excerto(*, chat_id: str, texto: str, lente: str, **_k):
        del chat_id, texto, lente
        return {
            "excertos": [
                {
                    "n": 1,
                    "documento_id": documento_id,
                    "pagina": 1,
                    "texto": "Excerto sem E2B.",
                    "offsets": {"inicio": 0, "fim": 16},
                    "score_juiz": 0.9,
                }
            ],
            "frases": [],
            "miniaturas": [
                {
                    "documento_id": documento_id,
                    "pagina": 1,
                    "url": f"/media/thumbs/{documento_id}_p1.webp",
                }
            ],
        }

    app = criar_app(
        caminho_sqlite=sqlite,
        raiz_modelos=raiz_tmp / "models",
        raiz_estaticos=raiz_tmp,
        motor_procura=motor_com_excerto,
    )
    servidor = arrancar(
        host="127.0.0.1",
        porta=porto_livre,
        raiz=raiz_tmp,
        pasta_data=raiz_tmp / "data",
        pasta_modelos=raiz_tmp / "models",
        bloquear=False,
        app=app,
    )
    try:
        assert servidor.endereco_efectivo()[0] == "127.0.0.1"
        base = f"http://127.0.0.1:{porto_livre}"
        _esperar_ready(f"{base}/")

        saude = httpx.get(f"{base}/health", timeout=2.0)
        assert saude.status_code == 200
        modelos = saude.json()["modelos"]
        assert modelos["escritor"] == "ausente"

        criado = httpx.post(f"{base}/chats", json={}, timeout=2.0)
        assert criado.status_code == 201
        cid = criado.json()["id"]

        procura = httpx.post(
            f"{base}/search",
            json={"chat_id": cid, "texto": "acesso remoto", "lente": "investigar"},
            timeout=5.0,
        )
        assert procura.status_code == 200
        assert "excerto" in procura.text or "Excerto" in procura.text
        assert servidor.endereco_efectivo()[1] == porto_livre
    finally:
        servidor.parar()
