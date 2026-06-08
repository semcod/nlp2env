#!/usr/bin/env bash
# 24+ wielojęzycznych promptów LLM (Ollama) → MCP → .env
set -euo pipefail

_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -n "${NLP2ENV_ROOT:-}" && -d "$NLP2ENV_ROOT/src" ]]; then
  ROOT="$NLP2ENV_ROOT"
else
  ROOT="$(cd "$_SCRIPT_DIR/../../.." && pwd)"
fi
# shellcheck source=examples/lib/common.sh
source "$ROOT/examples/lib/common.sh"

export SMTP_PASSWORD="${SMTP_PASSWORD:-e2e-test-secret-42}"
export NLP2ENV_EXAMPLE_DIR="$_SCRIPT_DIR"
export NLP2ENV_WORKDIR="${NLP2ENV_WORKDIR:-$_SCRIPT_DIR/workdir-multilang}"
export NLP2ENV_PROMPTS_FILE="${NLP2ENV_PROMPTS_FILE:-smtp-email-multilang.testql.toon.yaml}"
export NLP2ENV_PROMPTS_LOG="prompts-multilang.log.txt"
export NLP2ENV_LLM_ONLY=1
export NLP2ENV_FORCE_OLLAMA=1

echo "Cleaning up workdir: $NLP2ENV_WORKDIR"
rm -rf "$NLP2ENV_WORKDIR"

cd "$ROOT"
setup_example_env "$ROOT"

exec "$PYTHON" "$ROOT/examples/lib/run_smtp_prompts.py"
