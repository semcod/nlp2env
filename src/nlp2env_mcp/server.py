"""Stdio MCP server — read/write .env (email SMTP profile and custom keys)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from nlp2env.env_file import EnvFile, mask_value, resolve_env_path
from nlp2env.profiles import (
    EMAIL_PROFILE_KEYS,
    email_profile_from_dict,
    email_profile_status,
)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None  # type: ignore


def _ok(payload: dict[str, Any]) -> str:
    return json.dumps({"success": True, **payload}, ensure_ascii=False, indent=2)


def _err(message: str, **extra: Any) -> str:
    return json.dumps({"success": False, "error": message, **extra}, ensure_ascii=False, indent=2)


def _load(path: str | None = None) -> EnvFile:
    return EnvFile.load(path or os.getenv("NLP2ENV_ENV_FILE"))


def build_mcp() -> Any:
    if FastMCP is None:
        raise RuntimeError("mcp package required: pip install nlp2env[mcp]")

    mcp = FastMCP("nlp2env")

    @mcp.tool()
    def nlp2env_interfaces() -> str:
        """List nlp2env capabilities, env file path, and known profiles (email/SMTP)."""
        path = resolve_env_path()
        return _ok(
            {
                "name": "nlp2env",
                "env_file": str(path),
                "env_file_exists": path.is_file(),
                "profiles": {
                    "email": {
                        "description": "SMTP mailbox for nlp2dsl-worker / send_email workflows",
                        "keys": list(EMAIL_PROFILE_KEYS),
                    }
                },
                "tools": [
                    "nlp2env_interfaces",
                    "nlp2env_list",
                    "nlp2env_get",
                    "nlp2env_set",
                    "nlp2env_set_email",
                    "nlp2env_apply_text",
                    "nlp2env_backup",
                    "nlp2env_email_status",
                ],
                "env_vars": {
                    "NLP2ENV_ENV_FILE": "Path to target .env (default: ./.env or NLP2ENV_PROJECT_DIR/.env)",
                    "NLP2ENV_PROJECT_DIR": "Project root when NLP2ENV_ENV_FILE unset",
                },
            }
        )

    @mcp.tool()
    def nlp2env_list(env_file: str | None = None) -> str:
        """List keys in .env (secrets masked)."""
        env = _load(env_file)
        return _ok({"path": str(env.path), "values": env.list_masked()})

    @mcp.tool()
    def nlp2env_get(keys: str, env_file: str | None = None, unmask: bool = False) -> str:
        """Get one or more keys (comma-separated). Secrets masked unless unmask=true."""
        env = _load(env_file)
        result: dict[str, str | None] = {}
        for key in [k.strip() for k in keys.split(",") if k.strip()]:
            val = env.get(key)
            if val is None:
                result[key] = None
            elif unmask:
                result[key] = val
            else:
                result[key] = mask_value(key, val)
        return _ok({"path": str(env.path), "values": result})

    @mcp.tool()
    def nlp2env_set(values_json: str, env_file: str | None = None, overwrite: bool = True) -> str:
        """Set KEY=value pairs from JSON object, e.g. {\"SMTP_HOST\":\"smtp.gmail.com\"}."""
        try:
            data = json.loads(values_json)
        except json.JSONDecodeError as exc:
            return _err(f"Invalid JSON: {exc}")
        if not isinstance(data, dict):
            return _err("values_json must be a JSON object")
        env = _load(env_file)
        changed = env.set_many({str(k): str(v) for k, v in data.items()}, overwrite=overwrite)
        save_info = env.save(backup=True)
        return _ok(
            {
                "path": str(env.path),
                "changed": {k: mask_value(k, v) for k, v in changed.items()},
                "save": save_info,
            }
        )

    @mcp.tool()
    def nlp2env_set_email(
        host: str,
        user: str,
        password: str,
        port: str = "587",
        tls: str = "1",
        from_addr: str = "",
        env_file: str | None = None,
    ) -> str:
        """Save SMTP/email mailbox settings to .env (nlp2dsl-worker compatible)."""
        payload = email_profile_from_dict(
            {
                "host": host,
                "user": user,
                "password": password,
                "port": port,
                "tls": tls,
                "from": from_addr or user,
            }
        )
        env = _load(env_file)
        changed = env.set_many(payload)
        save_info = env.save(backup=True)
        status = email_profile_status(env.values)
        return _ok(
            {
                "path": str(env.path),
                "changed": {k: mask_value(k, v) for k, v in changed.items()},
                "email_status": {
                    **status,
                    "values": {k: mask_value(k, v) for k, v in status["values"].items()},
                },
                "save": save_info,
                "hint": "Restart nlp2dsl-worker after change: docker compose restart worker",
            }
        )

    @mcp.tool()
    def nlp2env_apply_text(text: str, env_file: str | None = None) -> str:
        """Apply KEY=value or 'KEY: value' lines from text block to .env."""
        env = _load(env_file)
        updates = env.apply_text(text)
        if not updates:
            return _err("No KEY=value lines found in text")
        changed = env.set_many(updates)
        save_info = env.save(backup=True)
        return _ok(
            {
                "path": str(env.path),
                "parsed": list(updates.keys()),
                "changed": {k: mask_value(k, v) for k, v in changed.items()},
                "save": save_info,
            }
        )

    @mcp.tool()
    def nlp2env_delete(keys: str, env_file: str | None = None) -> str:
        """Delete one or more keys (comma-separated) from .env."""
        env = _load(env_file)
        removed: list[str] = []
        missing: list[str] = []
        for key in [k.strip() for k in keys.split(",") if k.strip()]:
            if env.delete(key):
                removed.append(key)
            else:
                missing.append(key)
        save_info = env.save(backup=True)
        return _ok(
            {
                "path": str(env.path),
                "removed": removed,
                "missing": missing,
                "save": save_info,
            }
        )

    @mcp.tool()
    def nlp2env_backup(env_file: str | None = None) -> str:
        """Backup current .env before manual edits."""
        env = _load(env_file)
        dest = env.backup()
        if dest is None:
            return _err(f"File not found: {env.path}")
        return _ok({"path": str(env.path), "backup": str(dest)})

    @mcp.tool()
    def nlp2env_email_status(env_file: str | None = None) -> str:
        """Check whether SMTP/email profile is complete in .env."""
        env = _load(env_file)
        status = email_profile_status(env.values)
        masked = {k: mask_value(k, v) for k, v in status["values"].items()}
        return _ok({"path": str(env.path), "email_status": {**status, "values": masked}})

    return mcp


def main() -> None:
    build_mcp().run(transport="stdio")


if __name__ == "__main__":
    main()
