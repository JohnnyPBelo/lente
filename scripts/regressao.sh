#!/usr/bin/env bash
# Corre a suite de regressão a partir da raiz do repositório.
# Não descarrega modelos, não abre um porto e não altera o git.
set -euo pipefail

raiz="$(cd "$(dirname "$0")/.." && pwd)"
cd "$raiz"

export PYTHONDONTWRITEBYTECODE=1

python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' \
  || {
    echo "É preciso Python 3.11 ou superior para correr a regressão." >&2
    exit 1
  }

if ! python3 -m pytest --version >/dev/null 2>&1; then
  echo "O pytest não está instalado. Instale-o com «python3 -m pip install pytest» e volte a correr scripts/regressao.sh." >&2
  exit 1
fi

manifesto="tests/regressao/manifesto.txt"
if [[ ! -f "$manifesto" ]]; then
  echo "Não encontrei tests/regressao/manifesto.txt." >&2
  exit 1
fi

pytest_nodes=()
vitest_paths=()
while IFS= read -r linha || [[ -n "$linha" ]]; do
  linha="${linha#"${linha%%[![:space:]]*}"}"
  linha="${linha%"${linha##*[![:space:]]}"}"
  [[ -z "$linha" ]] && continue
  if [[ "$linha" == \#* ]]; then
    echo "O manifesto não aceita comentários: $linha" >&2
    exit 1
  fi
  if [[ "$linha" == *::* ]]; then
    pytest_nodes+=("$linha")
  else
    vitest_paths+=("$linha")
  fi
done < "$manifesto"

if ((${#pytest_nodes[@]})); then
  python3 -m pytest -p no:cacheprovider "${pytest_nodes[@]}"
fi

if ((${#vitest_paths[@]})); then
  if [[ ! -d apps/ui ]]; then
    echo "O manifesto lista testes de UI e apps/ui ainda não existe." >&2
    exit 1
  fi
  if [[ ! -f apps/ui/package.json ]]; then
    echo "apps/ui existe, mas não tem package.json para correr o Vitest." >&2
    exit 1
  fi
  (cd apps/ui && npx vitest run "${vitest_paths[@]}")
fi

python3 tests/regressao/exigir_agora.py
