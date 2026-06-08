"""Stdio MCP server — read/write .env (email SMTP profile and custom keys)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from nlp2env.env_file import EnvFile, mask_value, resolve_env_path
from nlp2env.validators import validate_key_value
from nlp2env.crypto import (
    decrypt_value,
    encrypt_value,
    generate_key,
    mask_encrypted,
    rotate_encrypted_values,
)
from nlp2env.profiles import (
    API_PROFILE_KEYS,
    DB_PROFILE_KEYS,
    EMAIL_PROFILE_KEYS,
    api_profile_from_dict,
    api_profile_status,
    db_profile_from_dict,
    db_profile_status,
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


def _resolve_password(
    password: str = "",
    password_env: str | None = None,
    password_file: str | None = None,
) -> tuple[str | None, str | None]:
    if password:
        return password, None
    if password_env:
        val = os.getenv(password_env, "").strip()
        if val:
            return val, None
        return None, f"Zmienna {password_env} nie jest ustawiona w środowisku MCP"
    if password_file:
        path = Path(password_file).expanduser()
        if path.is_file():
            return path.read_text(encoding="utf-8").strip(), None
        return None, f"Brak pliku hasła: {path}"
    return None, "Podaj password_env lub password_file — nie wklejaj hasła w czacie"


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
                },
                "api_keys": {
                    "description": "LLM/API keys for AI integrations",
                    "keys": list(API_PROFILE_KEYS),
                },
                "database": {
                    "description": "PostgreSQL, Redis, MongoDB connection strings",
                    "keys": list(DB_PROFILE_KEYS),
                },
            },
            "tools": [
                "nlp2env_interfaces",
                "nlp2env_list",
                "nlp2env_get",
                "nlp2env_set",
                "nlp2env_set_email",
                "nlp2env_set_api",
                "nlp2env_set_db",
                "nlp2env_apply_text",
                "nlp2env_delete",
                "nlp2env_backup",
                "nlp2env_email_status",
                "nlp2env_api_status",
                "nlp2env_db_status",
                "nlp2env_encrypt",
                "nlp2env_decrypt",
                "nlp2env_generate_key",
                "nlp2env_load_multi",
                "nlp2env_list_files",
                "nlp2env_migrate",
            ],
            "env_vars": {
                "NLP2ENV_ENV_FILE": "Path to target .env (default: ./.env or NLP2ENV_PROJECT_DIR/.env)",
                "NLP2ENV_MASTER_KEY": "Encryption key for encrypt/decrypt operations (or use ~/.nlp2env/key)",
                "NLP2ENV_PROJECT_DIR": "Project root when NLP2ENV_ENV_FILE unset",
            },
        }
    )


def nlp2env_list(env_file: str | None = None) -> str:
    """List keys in .env (secrets masked)."""
    env = _load(env_file)
    return _ok({"path": str(env.path), "values": env.list_masked()})


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


def _validate_values(values: dict[str, str]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for key, val in values.items():
        result = validate_key_value(key, val)
        if result and not result["ok"]:
            errors.append(result)
    return errors


def nlp2env_set(values_json: str, env_file: str | None = None, overwrite: bool = True, validate: bool = True) -> str:
    """Set KEY=value pairs from JSON object, e.g. {"SMTP_HOST":"smtp.gmail.com"}."""
    try:
        data = json.loads(values_json)
    except json.JSONDecodeError as exc:
        return _err(f"Invalid JSON: {exc}")
    if not isinstance(data, dict):
        return _err("values_json must be a JSON object")
    values = {str(k): str(v) for k, v in data.items()}
    if validate:
        errors = _validate_values(values)
        if errors:
            return _err("Validation failed", validation_errors=errors)
    env = _load(env_file)
    changed = env.set_many(values, overwrite=overwrite)
    save_info = env.save(backup=True)
    return _ok(
        {
            "path": str(env.path),
            "changed": {k: mask_value(k, v) for k, v in changed.items()},
            "save": save_info,
        }
    )


def nlp2env_set_email(
    host: str,
    user: str,
    password: str = "",
    port: str = "587",
    tls: str = "1",
    from_addr: str = "",
    password_env: str | None = None,
    password_file: str | None = None,
    env_file: str | None = None,
) -> str:
    """Save SMTP/email mailbox settings to .env (nlp2dsl-worker compatible).

    Prefer password_env=SMTP_PASSWORD (set before MCP start) instead of password in chat.
    """
    from nlp2env.validators import validate_email, validate_host, validate_port

    host_v = validate_host(host, field="SMTP_HOST")
    if not host_v["ok"]:
        return _err(f"SMTP_HOST: {host_v['rule']}")
    port_v = validate_port(port, field="SMTP_PORT")
    if not port_v["ok"]:
        return _err(f"SMTP_PORT: {port_v['rule']}")
    user_v = validate_email(user, field="SMTP_USER")
    if not user_v["ok"]:
        return _err(f"SMTP_USER: {user_v['rule']}")
    resolved, pwd_err = _resolve_password(password, password_env, password_file)
    if pwd_err:
        return _err(pwd_err)
    payload = email_profile_from_dict(
        {
            "host": host,
            "user": user,
            "password": resolved,
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


def nlp2env_backup(env_file: str | None = None) -> str:
    """Backup current .env before manual edits."""
    env = _load(env_file)
    dest = env.backup()
    if dest is None:
        return _err(f"File not found: {env.path}")
    return _ok({"path": str(env.path), "backup": str(dest)})


def nlp2env_email_status(env_file: str | None = None) -> str:
    """Check whether SMTP/email profile is complete in .env."""
    env = _load(env_file)
    status = email_profile_status(env.values)
    masked = {k: mask_value(k, v) for k, v in status["values"].items()}
    return _ok({"path": str(env.path), "email_status": {**status, "values": masked}})


def nlp2env_set_api(
    openai_api_key: str = "",
    anthropic_api_key: str = "",
    groq_api_key: str = "",
    huggingface_api_token: str = "",
    env_file: str | None = None,
) -> str:
    """Save LLM/API keys to .env. Pass only keys you want to set; empty strings are skipped."""
    payload = api_profile_from_dict(
        {
            "openai_api_key": openai_api_key or None,
            "anthropic_api_key": anthropic_api_key or None,
            "groq_api_key": groq_api_key or None,
            "huggingface_api_token": huggingface_api_token or None,
        }
    )
    if not payload:
        return _err("No API keys provided")
    env = _load(env_file)
    changed = env.set_many(payload)
    save_info = env.save(backup=True)
    status = api_profile_status(env.values)
    return _ok(
        {
            "path": str(env.path),
            "changed": {k: mask_value(k, v) for k, v in changed.items()},
            "api_status": {
                **status,
                "values": {k: mask_value(k, v) for k, v in status["values"].items()},
            },
            "save": save_info,
        }
    )


def nlp2env_api_status(env_file: str | None = None) -> str:
    """Check whether API key profile has any keys configured in .env."""
    env = _load(env_file)
    status = api_profile_status(env.values)
    masked = {k: mask_value(k, v) for k, v in status["values"].items()}
    return _ok({"path": str(env.path), "api_status": {**status, "values": masked}})


def nlp2env_set_db(
    postgres_host: str = "",
    postgres_port: str = "5432",
    postgres_db: str = "",
    postgres_user: str = "",
    postgres_password: str = "",
    redis_url: str = "",
    redis_host: str = "",
    redis_port: str = "6379",
    mongo_uri: str = "",
    env_file: str | None = None,
) -> str:
    """Save database connection settings to .env (PostgreSQL, Redis, MongoDB). Empty strings are skipped."""
    payload = db_profile_from_dict(
        {
            "postgres_host": postgres_host or None,
            "postgres_port": postgres_port or None,
            "postgres_db": postgres_db or None,
            "postgres_user": postgres_user or None,
            "postgres_password": postgres_password or None,
            "redis_url": redis_url or None,
            "redis_host": redis_host or None,
            "redis_port": redis_port or None,
            "mongo_uri": mongo_uri or None,
        }
    )
    if not payload:
        return _err("No database settings provided")
    env = _load(env_file)
    changed = env.set_many(payload)
    save_info = env.save(backup=True)
    status = db_profile_status(env.values)
    return _ok(
        {
            "path": str(env.path),
            "changed": {k: mask_value(k, v) for k, v in changed.items()},
            "db_status": {
                **status,
                "values": {k: mask_value(k, v) for k, v in status["values"].items()},
            },
            "save": save_info,
        }
    )


def nlp2env_db_status(env_file: str | None = None) -> str:
    """Check whether database profile is complete in .env."""
    env = _load(env_file)
    status = db_profile_status(env.values)
    masked = {k: mask_value(k, v) for k, v in status["values"].items()}
    return _ok({"path": str(env.path), "db_status": {**status, "values": masked}})


def nlp2env_load_multi(suffix: str = "local", env_file: str | None = None) -> str:
    """Load base .env and overlay .env.{suffix} (override wins)."""
    env = EnvFile.load_multi(env_file, suffix=suffix)
    base_path = resolve_env_path(env_file)
    suffix_path = resolve_env_path(env_file, suffix=suffix)
    sources: list[str] = []
    if base_path.is_file():
        sources.append(str(base_path))
    if suffix_path.is_file() and suffix_path != base_path:
        sources.append(str(suffix_path))
    return _ok(
        {
            "path": str(env.path),
            "suffix": suffix,
            "sources": sources,
            "values": env.list_masked(),
        }
    )


def nlp2env_list_files(project_dir: str | None = None) -> str:
    """List .env files in project directory (base .env + .env.*)."""
    root = Path(project_dir).expanduser().resolve() if project_dir else resolve_env_path().parent
    files = sorted(
        [str(p) for p in root.iterdir() if p.name.startswith(".env") and (p.is_file() or p.name == ".env")],
        key=lambda s: (not s.endswith(".env"), s),
    )
    return _ok({"project_dir": str(root), "files": files})


def nlp2env_generate_key() -> str:
    """Generate new Fernet encryption key. Save to ~/.nlp2env/key or set NLP2ENV_MASTER_KEY."""
    try:
        key = generate_key()
        return _ok({"key": key, "hint": "Save to ~/.nlp2env/key or export NLP2ENV_MASTER_KEY=<key>"})
    except RuntimeError as e:
        return _err(str(e))


def nlp2env_encrypt(plaintext: str) -> str:
    """Encrypt plaintext value, returns 'enc:<base64>' format."""
    try:
        encrypted = encrypt_value(plaintext)
        return _ok({"encrypted": encrypted, "masked": mask_encrypted(encrypted)})
    except RuntimeError as e:
        return _err(str(e))


def nlp2env_decrypt(ciphertext: str) -> str:
    """Decrypt 'enc:<base64>' value to plaintext."""
    try:
        decrypted = decrypt_value(ciphertext)
        return _ok({"decrypted": decrypted})
    except RuntimeError as e:
        return _err(str(e))


def nlp2env_migrate(
    keys: str,
    target_suffix: str,
    source_suffix: str = "",
    env_file: str | None = None,
    remove_from_source: bool = False,
) -> str:
    """Migrate keys from source .env to target .env.{suffix}. keys=comma-separated."""
    key_list = [k.strip() for k in keys.split(",") if k.strip()]
    if not key_list:
        return _err("No keys specified")
    if not target_suffix:
        return _err("target_suffix required (e.g., 'local', 'production')")

    source_path = resolve_env_path(env_file, suffix=source_suffix)
    target_path = resolve_env_path(env_file, suffix=target_suffix)

    if not source_path.is_file():
        return _err(f"Source env file not found: {source_path}")

    source_env = EnvFile.load(source_path)
    target_env = EnvFile.load(target_path) if target_path.is_file() else EnvFile(path=target_path)

    migrated: dict[str, str] = {}
    missing: list[str] = []
    for k in key_list:
        val = source_env.get(k)
        if val is None:
            missing.append(k)
            continue
        target_env.set(k, val)
        migrated[k] = mask_value(k, val)
        if remove_from_source:
            source_env.delete(k)

    if not migrated:
        return _err("No keys found to migrate", missing=missing)

    target_save = target_env.save(backup=True)
    source_save = source_env.save(backup=True) if remove_from_source else None

    return _ok(
        {
            "source": str(source_path),
            "target": str(target_path),
            "migrated": migrated,
            "missing_from_source": missing,
            "target_save": target_save,
            "source_save": source_save,
        }
    )


def build_mcp() -> Any:
    if FastMCP is None:
        raise RuntimeError("mcp package required: pip install nlp2env[mcp]")

    mcp = FastMCP("nlp2env")
    mcp.tool()(nlp2env_interfaces)
    mcp.tool()(nlp2env_list)
    mcp.tool()(nlp2env_get)
    mcp.tool()(nlp2env_set)
    mcp.tool()(nlp2env_set_email)
    mcp.tool()(nlp2env_apply_text)
    mcp.tool()(nlp2env_delete)
    mcp.tool()(nlp2env_backup)
    mcp.tool()(nlp2env_email_status)
    mcp.tool()(nlp2env_set_api)
    mcp.tool()(nlp2env_api_status)
    mcp.tool()(nlp2env_set_db)
    mcp.tool()(nlp2env_db_status)
    mcp.tool()(nlp2env_generate_key)
    mcp.tool()(nlp2env_encrypt)
    mcp.tool()(nlp2env_decrypt)
    mcp.tool()(nlp2env_load_multi)
    mcp.tool()(nlp2env_list_files)
    mcp.tool()(nlp2env_migrate)
    return mcp


def main() -> None:
    build_mcp().run(transport="stdio")


if __name__ == "__main__":
    main()
