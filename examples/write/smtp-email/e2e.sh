#!/usr/bin/env bash
# NL prompts from smtp-email.testql.toon.yaml → MCP → verify .env → append prompts.log.txt
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

export SMTP_PASSWORD="${SMTP_PASSWORD:-e2e-test-secret-42}"
export NLP2ENV_EXAMPLE_DIR="$EXAMPLE"
export NLP2ENV_PROMPTS_FILE="${NLP2ENV_PROMPTS_FILE:-smtp-email-inline.testql.toon.yaml}"
export NLP2ENV_WORKDIR="$WORKDIR"

echo "Cleaning up workdir: $WORKDIR"
rm -rf "$WORKDIR"

cd "$ROOT"
setup_example_env "$ROOT"

exec "$PYTHON" "$ROOT/examples/lib/run_smtp_prompts.py"
