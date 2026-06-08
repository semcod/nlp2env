#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=examples/lib/common.sh
source "$ROOT/examples/lib/common.sh"
setup_example_env "$ROOT"

cd "$ROOT"

echo "== pytest ($PYTHON) =="
if [[ -x "${PYTHON%/python}/pytest" ]]; then
  "${PYTHON%/python}/pytest" tests/ -q
else
  "$PYTHON" -m pytest tests/ -q
fi

echo "== scripts/test-mcp-live.sh =="
bash scripts/test-mcp-live.sh

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

if [[ "${NLP2ENV_RUN_MULTILANG:-}" == "1" ]]; then
    echo "== examples/write/smtp-email/e2e-multilang.sh =="
    export SMTP_PASSWORD="${SMTP_PASSWORD:-e2e-test-secret-42}"
    bash examples/write/smtp-email/e2e-multilang.sh
fi

echo "ALL EXAMPLES OK"
