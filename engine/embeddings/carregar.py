"""Carga do EmbeddingGemma 2 só-texto; caminho local se HF falhar."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

from engine.embeddings.dispositivo import (
    DTYPE_CPU,
    DTYPE_PROIBIDO,
    dtype_para,
    validar_dtype,
)

MODELO_ID = "google/embeddinggemma-2"
PASTA_MODELO = "embeddinggemma-2"
DIMENSAO_NATIVA = 768
DIMENSAO = 256
CONFIG_TEXTO_ONLY: dict[str, None] = {
    "vision_config": None,
    "audio_config": None,
}


class PesosEmbeddingAusentes(Exception):
    """Pesos em falta; a app pode abrir com caminho manual (PLN-21)."""

    def __init__(self, caminho_manual: str) -> None:
        self.caminho_manual = caminho_manual
        super().__init__(
            "Pesos do EmbeddingGemma ausentes. "
            f"Coloque o modelo texto-only em: {caminho_manual}"
        )


@dataclass
class SessaoEmbedding:
    """Sessão residente do EmbeddingGemma (congelado, só texto)."""

    modelo_id: str
    caminho: Path
    dispositivo: str
    dtype: str
    vision_config: Any
    audio_config: Any
    _modelo: Any

    def encode(self, textos: str | Sequence[str]) -> list[list[float]]:
        """Devolve vectores nativos (768d) via o modelo injectado ou real."""
        unico = isinstance(textos, str)
        lote = [textos] if unico else list(textos)
        bruto = self._modelo.encode(lote)
        vectores = [_como_lista(v) for v in bruto]
        return vectores[0:1] if unico else vectores


# Sessões residentes partilhadas no processo (ingest + procura).
# Sem isto, cada POST /library/ingest volta a carregar ~1,5 GB de pesos e
# pode matar o processo (OOM) a meio de um stress run.
_CACHE_SESSOES: dict[tuple[str, str], SessaoEmbedding] = {}


def limpar_cache_sessoes() -> None:
    """Esvazia o cache (testes / reinício controlado)."""
    _CACHE_SESSOES.clear()


def pasta_embedding(raiz_modelos: Path | str | None = None) -> Path:
    """Pasta runtime: ``models/embeddinggemma-2/`` (fora do git)."""
    raiz = Path(raiz_modelos) if raiz_modelos is not None else Path("models")
    return Path(raiz) / PASTA_MODELO


def caminho_pesos(raiz_modelos: Path | str | None = None) -> Path:
    """Caminho manual indicado quando o download HF falha ou falta."""
    return pasta_embedding(raiz_modelos)


def carregar_modelo(
    *,
    raiz_modelos: Path | str | None = None,
    dispositivo: str | None = None,
    modelo: Any | None = None,
    factory: Callable[..., Any] | None = None,
    tem_gpu: bool = False,
) -> SessaoEmbedding:
    """Carrega (ou aceita double de) EmbeddingGemma texto-only.

    Não descarrega pesos da rede. Se a pasta local faltar e não houver
    ``modelo`` injectado, levanta ``PesosEmbeddingAusentes`` com o caminho.
    ``factory`` permite espiar kwargs de carga nos testes (sem HF).
    """
    from engine.embeddings.dispositivo import escolher_dispositivo

    destino = caminho_pesos(raiz_modelos)
    disp = dispositivo or escolher_dispositivo(tem_gpu=tem_gpu)
    dtype = validar_dtype(dtype_para(disp))
    if dtype == DTYPE_PROIBIDO:
        raise RuntimeError("caminho float16 não é usado")

    # Doubles injectados (modelo=/factory=) nunca entram no cache residente.
    usar_cache = modelo is None and factory is None
    chave = (str(destino.resolve()), disp)
    if usar_cache and chave in _CACHE_SESSOES:
        return _CACHE_SESSOES[chave]

    if modelo is None:
        if not _pasta_tem_pesos(destino):
            raise PesosEmbeddingAusentes(str(destino))
        criador = factory or _factory_sentence_transformers
        modelo = criador(
            str(destino),
            config_kwargs=dict(CONFIG_TEXTO_ONLY),
            truncate_dim=DIMENSAO,
            model_kwargs={"torch_dtype": _torch_dtype(dtype)},
            device=disp,
        )

    vision = getattr(modelo, "vision_config", None)
    audio = getattr(modelo, "audio_config", None)
    if vision is None and hasattr(modelo, "config"):
        vision = getattr(modelo.config, "vision_config", None)
        audio = getattr(modelo.config, "audio_config", None)

    sessao = SessaoEmbedding(
        modelo_id=MODELO_ID,
        caminho=destino,
        dispositivo=disp,
        dtype=dtype,
        vision_config=vision,
        audio_config=audio,
        _modelo=modelo,
    )
    if usar_cache:
        _CACHE_SESSOES[chave] = sessao
    return sessao


def embutir(
    texto: str,
    *,
    sessao: SessaoEmbedding,
    ja_prefixado: bool = True,
) -> list[float]:
    """Embedding 256d L2-normalizado em float32 lógico; sem caminho float16."""
    if sessao.dtype == DTYPE_PROIBIDO:
        raise RuntimeError("float16 proibido no caminho de embedding")
    validar_dtype(sessao.dtype)

    nativo = sessao.encode(texto)[0]
    if len(nativo) < DIMENSAO:
        raise ValueError(
            f"vector nativo demasiado curto: {len(nativo)} < {DIMENSAO}"
        )
    # Matryoshka: cortar 256 e renormalizar L2 (obrigatório).
    cortado = nativo[:DIMENSAO]
    return _normalizar_l2(_para_float32(cortado))


def _pasta_tem_pesos(pasta: Path) -> bool:
    if not pasta.is_dir():
        return False
    marcadores = (
        "config.json",
        "model.safetensors",
        "pytorch_model.bin",
        "model.onnx",
    )
    return any((pasta / nome).is_file() for nome in marcadores)


def _factory_sentence_transformers(caminho: str, **kwargs: Any) -> Any:
    """Carga real dos pesos locais.

    sentence-transformers 6.2+ carrega EmbeddingGemma 2 mas falha em
    ``encode`` (processor sem chat template). Usamos sempre
    ``transformers.AutoModel`` para o caminho de produto.
    """
    model_kwargs = dict(kwargs.pop("model_kwargs", {}) or {})
    torch_dtype = model_kwargs.get("torch_dtype")
    if torch_dtype is not None and str(torch_dtype).endswith("float16"):
        raise RuntimeError("float16 proibido na carga do EmbeddingGemma")
    return _factory_transformers_direct(
        caminho, **kwargs, model_kwargs=model_kwargs
    )


def _factory_transformers_direct(caminho: str, **kwargs: Any) -> Any:
    """AutoModel texto-only com ``.encode`` → vectores nativos 768d."""
    import torch
    from transformers import AutoModel, AutoTokenizer

    model_kwargs = kwargs.get("model_kwargs", {}) or {}
    device = kwargs.get("device", "cpu")
    if isinstance(device, torch.device):
        device = device.type

    modelo = AutoModel.from_pretrained(
        caminho,
        torch_dtype=model_kwargs.get("torch_dtype", torch.float32),
        trust_remote_code=True,
    ).to(device)
    modelo.eval()
    tokenizador = AutoTokenizer.from_pretrained(caminho, trust_remote_code=True)

    class DirectEmbedder:
        def __init__(self, model: Any, tokenizer: Any, device_name: str) -> None:
            self.model = model
            self.tokenizer = tokenizer
            self.device = device_name
            self.vision_config = None
            self.audio_config = None

        def encode(self, textos: str | list[str]) -> list[list[float]]:
            lote = [textos] if isinstance(textos, str) else list(textos)
            with torch.no_grad():
                entradas = self.tokenizer(
                    lote,
                    padding=True,
                    truncation=True,
                    return_tensors="pt",
                    max_length=512,
                ).to(self.device)
                saidas = self.model(**entradas)
                token_emb = saidas.last_hidden_state
                mascara = entradas["attention_mask"].unsqueeze(-1).expand(token_emb.size()).float()
                soma = torch.sum(token_emb * mascara, 1)
                dens = torch.clamp(mascara.sum(1), min=1e-9)
                sent = soma / dens
                sent = torch.nn.functional.normalize(sent, p=2, dim=1)
                return sent.cpu().numpy().tolist()

    return DirectEmbedder(modelo, tokenizador, device)


def _torch_dtype(dtype: str) -> Any:
    """Mapeia dtype de produto para objecto torch, se torch existir."""
    try:
        import torch
    except ImportError:
        return dtype
    if dtype == "bfloat16":
        return torch.bfloat16
    return torch.float32


def _como_lista(vector: Any) -> list[float]:
    if hasattr(vector, "tolist"):
        return [float(x) for x in vector.tolist()]
    return [float(x) for x in vector]


def _para_float32(valores: list[float]) -> list[float]:
    # float() em Python é IEEE double, mas o contrato de produto é float32:
    # truncamos via struct para matar NaN de half e fixar precisão.
    import array
    import math

    buf = array.array("f", (0.0 if math.isnan(v) else float(v) for v in valores))
    return [float(x) for x in buf]


def _normalizar_l2(valores: list[float]) -> list[float]:
    import math

    norma = math.sqrt(sum(v * v for v in valores))
    if norma == 0.0:
        return list(valores)
    return [v / norma for v in valores]


__all__ = [
    "CONFIG_TEXTO_ONLY",
    "DIMENSAO",
    "DIMENSAO_NATIVA",
    "MODELO_ID",
    "PASTA_MODELO",
    "PesosEmbeddingAusentes",
    "SessaoEmbedding",
    "caminho_pesos",
    "carregar_modelo",
    "embutir",
    "limpar_cache_sessoes",
    "pasta_embedding",
]
