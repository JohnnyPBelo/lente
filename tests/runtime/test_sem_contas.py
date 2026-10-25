"""Regressões REG-FOR-008 / REG-FOR-009: sem contas e sem áudio."""

from __future__ import annotations

from pathlib import Path

from starlette.testclient import TestClient

from engine.api.app import criar_app
from engine.embeddings.carregar import CONFIG_TEXTO_ONLY


def _caminhos_rotas(app) -> set[str]:
    caminhos: set[str] = set()
    for rota in app.routes:
        caminho = getattr(rota, "path", None)
        if isinstance(caminho, str):
            caminhos.add(caminho)
        # Mounts
        nome = getattr(rota, "name", "")
        if nome:
            caminhos.add(str(nome))
    return caminhos


def test_reg_for_008(caminho_tmp: Path) -> None:
    """Superfície HTTP sem login, papéis nem sincronização."""
    app = criar_app(caminho_sqlite=caminho_tmp)
    caminhos = " ".join(sorted(_caminhos_rotas(app))).lower()
    for proibido in (
        "login",
        "logout",
        "signup",
        "oauth",
        "permission",
        "role",
        "sync",
        "account",
        "conta",
        "sessao",
        "session",
    ):
        assert proibido not in caminhos, f"rota proibida: {proibido}"

    cliente = TestClient(app)
    for path in ("/login", "/auth", "/sync", "/accounts"):
        resposta = cliente.get(path)
        assert resposta.status_code in {404, 405}


def test_reg_for_009() -> None:
    """Sem ditado, voz nem pesos de áudio no runtime."""
    assert CONFIG_TEXTO_ONLY.get("audio_config") is None
    assert CONFIG_TEXTO_ONLY.get("vision_config") is None

    raiz = Path(__file__).resolve().parents[2]
    # Inventário grosseiro: UI e motor não anunciam modalidades de áudio.
    fontes = [
        (raiz / "apps" / "ui" / "src" / "lib" / "copy.ts").read_text(
            encoding="utf-8"
        ),
        (raiz / "engine" / "embeddings" / "carregar.py").read_text(
            encoding="utf-8"
        ),
        (raiz / "engine" / "cli.py").read_text(encoding="utf-8"),
    ]
    junto = "\n".join(fontes).lower()
    for termo in ("ditado", "dictation", "speech-to-text", "whisper", "microfone"):
        assert termo not in junto
