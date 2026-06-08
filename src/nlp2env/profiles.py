"""Known .env profiles for common integrations."""

from __future__ import annotations

from typing import Any

EMAIL_PROFILE_KEYS = (
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "SMTP_TLS",
    "SMTP_FROM",
    "SMTP_TIMEOUT",
)

EMAIL_PROFILE_DEFAULTS: dict[str, str] = {
    "SMTP_PORT": "587",
    "SMTP_TLS": "1",
    "SMTP_TIMEOUT": "30",
    "SMTP_FROM": "nlp2dsl@localhost",
}

API_PROFILE_KEYS = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GROQ_API_KEY",
    "HUGGINGFACE_API_TOKEN",
)

API_PROFILE_DEFAULTS: dict[str, str] = {}


def _map_profile(data: dict[str, Any], mapping: dict[str, str], profile_keys: tuple[str, ...]) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw_key, val in data.items():
        if val is None:
            continue
        key = mapping.get(raw_key.lower(), raw_key.upper())
        if key in profile_keys:
            out[key] = str(val).strip()
    return out


def email_profile_from_dict(data: dict[str, Any]) -> dict[str, str]:
    """Normalize email/SMTP settings from MCP tool arguments."""
    mapping = {
        "host": "SMTP_HOST",
        "smtp_host": "SMTP_HOST",
        "port": "SMTP_PORT",
        "smtp_port": "SMTP_PORT",
        "user": "SMTP_USER",
        "smtp_user": "SMTP_USER",
        "username": "SMTP_USER",
        "password": "SMTP_PASSWORD",
        "smtp_password": "SMTP_PASSWORD",
        "tls": "SMTP_TLS",
        "smtp_tls": "SMTP_TLS",
        "from": "SMTP_FROM",
        "from_addr": "SMTP_FROM",
        "smtp_from": "SMTP_FROM",
        "timeout": "SMTP_TIMEOUT",
        "smtp_timeout": "SMTP_TIMEOUT",
    }
    out = _map_profile(data, mapping, EMAIL_PROFILE_KEYS)
    for key, default in EMAIL_PROFILE_DEFAULTS.items():
        out.setdefault(key, default)
    return out


def email_profile_status(values: dict[str, str]) -> dict[str, Any]:
    missing = [k for k in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD") if not values.get(k)]
    return {
        "profile": "email",
        "keys": list(EMAIL_PROFILE_KEYS),
        "configured": not missing,
        "missing": missing,
        "values": {k: values.get(k, "") for k in EMAIL_PROFILE_KEYS},
    }


def api_profile_from_dict(data: dict[str, Any]) -> dict[str, str]:
    """Normalize API key settings from MCP tool arguments."""
    mapping = {
        "openai_api_key": "OPENAI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "groq_api_key": "GROQ_API_KEY",
        "groq": "GROQ_API_KEY",
        "huggingface_api_token": "HUGGINGFACE_API_TOKEN",
        "huggingface": "HUGGINGFACE_API_TOKEN",
    }
    out = _map_profile(data, mapping, API_PROFILE_KEYS)
    for key, default in API_PROFILE_DEFAULTS.items():
        out.setdefault(key, default)
    return out


def api_profile_status(values: dict[str, str]) -> dict[str, Any]:
    missing = [k for k in API_PROFILE_KEYS if not values.get(k)]
    return {
        "profile": "api_keys",
        "keys": list(API_PROFILE_KEYS),
        "configured": len(missing) < len(API_PROFILE_KEYS),
        "missing": missing,
        "values": {k: values.get(k, "") for k in API_PROFILE_KEYS},
    }


DB_PROFILE_KEYS = (
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "REDIS_URL",
    "REDIS_HOST",
    "REDIS_PORT",
    "MONGO_URI",
)

DB_PROFILE_DEFAULTS: dict[str, str] = {
    "POSTGRES_PORT": "5432",
    "REDIS_PORT": "6379",
}


def db_profile_from_dict(data: dict[str, Any]) -> dict[str, str]:
    """Normalize database settings from MCP tool arguments."""
    mapping = {
        "postgres_host": "POSTGRES_HOST",
        "pg_host": "POSTGRES_HOST",
        "postgres_port": "POSTGRES_PORT",
        "pg_port": "POSTGRES_PORT",
        "postgres_db": "POSTGRES_DB",
        "pg_db": "POSTGRES_DB",
        "database": "POSTGRES_DB",
        "postgres_user": "POSTGRES_USER",
        "pg_user": "POSTGRES_USER",
        "postgres_password": "POSTGRES_PASSWORD",
        "pg_password": "POSTGRES_PASSWORD",
        "redis_url": "REDIS_URL",
        "redis_host": "REDIS_HOST",
        "redis_port": "REDIS_PORT",
        "mongo_uri": "MONGO_URI",
        "mongodb_uri": "MONGO_URI",
    }
    out = _map_profile(data, mapping, DB_PROFILE_KEYS)
    for key, default in DB_PROFILE_DEFAULTS.items():
        out.setdefault(key, default)
    return out


def db_profile_status(values: dict[str, str]) -> dict[str, Any]:
    pg_required = ("POSTGRES_HOST", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD")
    pg_missing = [k for k in pg_required if not values.get(k)]
    redis_ok = bool(values.get("REDIS_URL") or values.get("REDIS_HOST"))
    mongo_ok = bool(values.get("MONGO_URI"))
    return {
        "profile": "database",
        "keys": list(DB_PROFILE_KEYS),
        "configured": not pg_missing,
        "missing": pg_missing,
        "redis": redis_ok,
        "mongo": mongo_ok,
        "values": {k: values.get(k, "") for k in DB_PROFILE_KEYS},
    }
