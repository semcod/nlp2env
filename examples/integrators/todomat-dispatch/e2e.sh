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
touch "$ENV_FILE"

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
from todomat_parse import parse_mcp_command

env_file = os.environ["NLP2ENV_ENV_FILE"]

prompts = [
    "nlp2env_set_email: host=smtp.test.local, user=u@t.c, password_env=SMTP_PASSWORD, port=587",
    "nlp2env_email_status",
    "nlp2env_list",
    "nlp2env_apply_text: text=APP_NAME=todomat-demo",
]

for prompt in prompts:
    cmd = parse_mcp_command(prompt)
    assert cmd is not None, f"parse failed: {prompt!r}"
    assert cmd["server"] == "nlp2env", cmd
    tool = cmd["tool"]
    args = cmd["arguments"]

    if tool == "nlp2env_set_email":
        assert_ok(mcp_call(tool, args, env_file=env_file), tool)
    elif tool == "nlp2env_email_status":
        status = assert_ok(mcp_call(tool, args, env_file=env_file), tool)
        assert status["email_status"]["configured"] is True
    elif tool == "nlp2env_list":
        listed = assert_ok(mcp_call(tool, args, env_file=env_file), tool)
        assert "SMTP_HOST" in listed["values"]
    elif tool == "nlp2env_apply_text":
        assert_ok(mcp_call(tool, args, env_file=env_file), tool)
    else:
        raise AssertionError(f"unexpected tool {tool}")

text = Path(env_file).read_text(encoding="utf-8")
for needle in (
    "SMTP_HOST=smtp.test.local",
    "SMTP_USER=u@t.c",
    "SMTP_PASSWORD=dispatch-test-secret",
    "APP_NAME=todomat-demo",
):
    assert needle in text, f"missing {needle!r}"

print("examples/integrators/todomat-dispatch: OK")
PY
