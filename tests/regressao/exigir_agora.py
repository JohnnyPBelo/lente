#!/usr/bin/env python3
"""Falha se um REG marcado como agora na cobertura não estiver no manifesto."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import apoio


def main() -> int:
    faltam = apoio.reg_agora_em_falta()
    if not faltam:
        return 0
    print(
        "Há regressões marcadas como agora que não estão no manifesto:",
        file=sys.stderr,
    )
    for item in faltam:
        print(f"  {item}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
