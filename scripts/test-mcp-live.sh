#!/usr/bin/env bash
# Live MCP stdio test for nlp2env-mcp.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEST_ENV="${TEST_ENV:-/tmp/nlp2env-mcp-test.env}"
rm -f "$TEST_ENV"

export NLP2ENV_ENV_FILE="$TEST_ENV"
export PATH="${ROOT}/venv/bin:${PATH}"

python3 - <<'PY'
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> int:
    env = os.environ.copy()
    params = StdioServerParameters(command="nlp2env-mcp", args=[], env=env)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = sorted(t.name for t in tools.tools)
            print("tools:", ", ".join(names))
            assert "nlp2env_set_email" in names

            r1 = await session.call_tool(
                "nlp2env_set_email",
                {
                    "host": "smtp.test.local",
                    "user": "jan@firma.pl",
                    "password": "test-secret",
                    "port": "587",
                    "from_addr": "jan@firma.pl",
                },
            )
            text1 = "".join(b.text for b in r1.content if hasattr(b, "text"))
            data1 = json.loads(text1)
            assert data1["success"], data1
            print("set_email: OK")

            r2 = await session.call_tool("nlp2env_email_status", {})
            text2 = "".join(b.text for b in r2.content if hasattr(b, "text"))
            data2 = json.loads(text2)
            assert data2["email_status"]["configured"] is True
            print("email_status: configured")

            r3 = await session.call_tool("nlp2env_get", {"keys": "SMTP_HOST,SMTP_USER"})
            text3 = "".join(b.text for b in r3.content if hasattr(b, "text"))
            data3 = json.loads(text3)
            assert data3["values"]["SMTP_HOST"] == "smtp.test.local"
            print("get: OK")
    return 0


raise SystemExit(asyncio.run(main()))
PY

echo "env file: $TEST_ENV"
grep -E '^SMTP_' "$TEST_ENV"
echo "MCP live test PASSED"
