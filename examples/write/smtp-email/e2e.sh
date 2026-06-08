#!/usr/bin/env bash
# NL prompt → nlp2env_set_email → verify .env (symuluje agenta Cursor/todomat)
set -euo pipefail

_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -n "${NLP2ENV_ROOT:-}" && -d "$NLP2ENV_ROOT/src" ]]; then
  ROOT="$NLP2ENV_ROOT"
else
  ROOT="$(cd "$_SCRIPT_DIR/../../.." && pwd)"
fi
# shellcheck source=examples/lib/common.sh
source "$ROOT/examples/lib/common.sh"
PYTHON="$(resolve_python "$ROOT")"
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

set -a
# shellcheck source=/dev/null
source "$EXAMPLE/prompts.env"
set +a
export NLP2ENV_ENV_FILE="$ENV_FILE"

cd "$ROOT"
export PATH="${ROOT}/.venv/bin:${ROOT}/venv/bin:/usr/local/bin:${PATH}"
export PYTHONPATH="$ROOT/examples/lib:${PYTHONPATH:-}"

"$PYTHON" - <<'PY'
import os
from pathlib import Path

from run_mcp import assert_ok, mcp_call

env_file = os.environ["NLP2ENV_ENV_FILE"]

out = assert_ok(
    mcp_call(
        "nlp2env_set_email",
        {
            "host": "smtp.gmail.com",
            "user": "jan@firma.pl",
            "password_env": "SMTP_PASSWORD",
            "port": "587",
            "from_addr": "jan@firma.pl",
        },
        env_file=env_file,
    ),
    "set_email",
)
assert out["email_status"]["configured"] is True

status = assert_ok(mcp_call("nlp2env_email_status", env_file=env_file), "email_status")
assert status["email_status"]["configured"] is True

text = Path(env_file).read_text(encoding="utf-8")
for needle in (
    "SMTP_HOST=smtp.gmail.com",
    "SMTP_USER=jan@firma.pl",
    "SMTP_PORT=587",
    "SMTP_PASSWORD=e2e-test-secret-42",
):
    assert needle in text, f"missing {needle!r} in:\n{text}"

print("examples/write/smtp-email: OK")
PY
