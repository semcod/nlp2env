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
touch "$ENV_FILE"
export NLP2ENV_ENV_FILE="$ENV_FILE"

cd "$ROOT"
setup_example_env "$ROOT"

"$PYTHON" - <<'PY'
import json
import os
from pathlib import Path

from run_mcp import assert_ok, mcp_call

env_file = os.environ["NLP2ENV_ENV_FILE"]

payload = json.dumps(
    {
        "DATABASE_URL": "postgres://localhost:5432/app",
        "REDIS_URL": "redis://localhost:6379/0",
    }
)
assert_ok(mcp_call("nlp2env_set", {"values_json": payload}, env_file=env_file), "set")

listed = assert_ok(mcp_call("nlp2env_list", env_file=env_file), "list")
assert "DATABASE_URL" in listed["values"]
assert "REDIS_URL" in listed["values"]

text = Path(env_file).read_text(encoding="utf-8")
assert "DATABASE_URL=postgres://localhost:5432/app" in text
assert "REDIS_URL=redis://localhost:6379/0" in text

print("examples/write/custom-keys: OK")
PY
