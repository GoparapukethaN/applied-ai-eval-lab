#!/usr/bin/env bash
set -euo pipefail

if [[ -x ".venv/bin/python" ]]; then
  python_cmd=".venv/bin/python"
else
  python_cmd="${PYTHON:-python3}"
fi

"$python_cmd" -m pytest backend/tests

(
  cd frontend
  npm audit --audit-level=moderate
  npm run typecheck
  npm run build
  npm run build:pages
)

docker compose config --quiet

echo "local verification passed"
