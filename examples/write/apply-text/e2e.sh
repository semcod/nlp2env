#!/usr/bin/env bash
set -euo pipefail

_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -n "${NLP2ENV_ROOT:-}" && -d "$NLP2ENV_ROOT/src" ]]; then
  ROOT="$NLP2ENV_ROOT"
else
  ROOT="$(cd "$_SCRIPT_DIR/../../.." && pwd)"
fi
# shellcheck source=examples/lib/common.sh
source "$ROOT/examples/lib/common.sh"
EXAMPLE="$_SCRIPT_DIR"
EXAMPLE_NAME="$(basename "$EXAMPLE")"
if [[ -n "${NLP2ENV_ROOT:-}" ]]; then
  WORKDIR="${WORKDIR:-/tmp/nlp2env-e2e/$EXAMPLE_NAME}"
else
  WORKDIR="${WORKDIR:-$EXAMPLE/workdir}"
fi
ENV_FILE="$WORKDIR/.env"

rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"
cp "$EXAMPLE/.env.example" "$ENV_FILE"
export NLP2ENV_ENV_FILE="$ENV_FILE"

cd "$ROOT"
setup_example_env "$ROOT"

"$PYTHON" - <<'PY'
import os
from pathlib import Path

from run_mcp import assert_ok, mcp_call

env_file = os.environ["NLP2ENV_ENV_FILE"]

block = """\
API_URL=https://api.firma.pl
LOG_LEVEL=debug
SMTP_HOST=smtp.office365.com
SMTP_PORT: 587
"""

out = assert_ok(mcp_call("nlp2env_apply_text", {"text": block}, env_file=env_file), "apply_text")
assert set(out["parsed"]) >= {"API_URL", "LOG_LEVEL", "SMTP_HOST", "SMTP_PORT"}

text = Path(env_file).read_text(encoding="utf-8")
for needle in (
    "API_URL=https://api.firma.pl",
    "LOG_LEVEL=debug",
    "SMTP_HOST=smtp.office365.com",
    "SMTP_PORT=587",
    "EXISTING_KEY=keep-me",
):
    assert needle in text, f"missing {needle!r}"

print("examples/write/apply-text: OK")
PY
