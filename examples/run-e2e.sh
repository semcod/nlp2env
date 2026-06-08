#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== pytest =="
.venv/bin/pytest tests/ -q 2>/dev/null || python3 -m pytest tests/ -q

echo "== scripts/test-mcp-live.sh =="
PATH="${ROOT}/.venv/bin:${ROOT}/venv/bin:${PATH}" bash scripts/test-mcp-live.sh

for script in \
    examples/write/smtp-email/e2e.sh \
    examples/write/apply-text/e2e.sh \
    examples/write/custom-keys/e2e.sh \
    examples/integrators/mcp-stdio/e2e.sh \
    examples/integrators/todomat-dispatch/e2e.sh
do
    echo "== $script =="
    chmod +x "$script"
    bash "$script"
done

echo "ALL EXAMPLES OK"
