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
WORKDIR="${WORKDIR:-/tmp/nlp2env-mcp-stdio-e2e}"
ENV_FILE="$WORKDIR/.env"

rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"
export NLP2ENV_ENV_FILE="$ENV_FILE"
export PATH="${ROOT}/.venv/bin:${ROOT}/venv/bin:/usr/local/bin:${PATH}"
export PYTHONPATH="$ROOT/examples/lib:${PYTHONPATH:-}"

cd "$ROOT"

"$PYTHON" - <<'PY'
import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from run_mcp import _mcp_command


async def main() -> None:
    env = os.environ.copy()
    params = StdioServerParameters(command=_mcp_command(), args=[], env=env)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
            for required in (
                "nlp2env_interfaces",
                "nlp2env_set_email",
                "nlp2env_apply_text",
                "nlp2env_set",
                "nlp2env_list",
            ):
                assert required in names, f"missing tool {required}"

            r = await session.call_tool("nlp2env_interfaces", {})
            text = "".join(b.text for b in r.content if hasattr(b, "text"))
            data = json.loads(text)
            assert data["success"] is True
            assert data["env_file"] == os.environ["NLP2ENV_ENV_FILE"]


asyncio.run(main())
print("examples/integrators/mcp-stdio: OK")
PY
