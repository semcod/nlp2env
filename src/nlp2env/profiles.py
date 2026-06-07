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
    out: dict[str, str] = {}
    for raw_key, val in data.items():
        if val is None:
            continue
        key = mapping.get(raw_key.lower(), raw_key.upper())
        if key in EMAIL_PROFILE_KEYS:
            out[key] = str(val).strip()
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
