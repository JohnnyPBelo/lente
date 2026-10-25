"""Fila de indexação: um documento activo de cada vez."""

from __future__ import annotations

import threading
from collections import deque


class FilaIngestao:
    """Enfileira documentos e só liberta o próximo quando o actual termina."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._fila: deque[str] = deque()
        self._activo: str | None = None

    def enfileirar(self, documento_id: str) -> None:
        with self._lock:
            self._fila.append(documento_id)

    def proximo(self) -> str | None:
        """Devolve o próximo documento só se nenhum estiver activo."""
        with self._lock:
            if self._activo is not None:
                return None
            if not self._fila:
                return None
            self._activo = self._fila.popleft()
            return self._activo

    def concluir(self, documento_id: str) -> None:
        with self._lock:
            if self._activo != documento_id:
                raise RuntimeError(
                    f"O documento activo é {self._activo!r}, "
                    f"não {documento_id!r}."
                )
            self._activo = None

    @property
    def activo(self) -> str | None:
        with self._lock:
            return self._activo

    def pendentes(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(self._fila)
