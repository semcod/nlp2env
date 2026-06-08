"""Validate common .env value formats."""

from __future__ import annotations

import re
from typing import Any

_EMAIL_RE = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

_URL_RE = re.compile(
    r"^(https?|ftp|sftp|mqtt|ws|wss)://"
    r"([A-Za-z0-9.-]+|\[[0-9a-fA-F:]+\])"
    r"(:[0-9]{1,5})?"
    r"(/.*)?$"
)

_HOST_RE = re.compile(
    r"^([A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?\.)*"
    r"[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?$"
)

_IP_RE = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)

_PORT_RE = re.compile(r"^\d{1,5}$")

_BOOL_RE = re.compile(r"^(1|0|true|false|yes|no|on|off)$", re.I)

_OPENAI_KEY_RE = re.compile(r"^sk-[A-Za-z0-9_-]+$")
_GROQ_KEY_RE = re.compile(r"^gsk-[A-Za-z0-9_-]+$")
_ANTHROPIC_KEY_RE = re.compile(r"^sk-ant-api03-[A-Za-z0-9_-]+$")
_HF_TOKEN_RE = re.compile(r"^hf_[A-Za-z0-9]+$")

_DOMAIN_RE = re.compile(
    r"^([A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,}$"
)


def _err(field: str, value: str, rule: str) -> dict[str, Any]:
    return {"field": field, "value": value, "rule": rule, "ok": False}


def validate_email(value: str, field: str = "email") -> dict[str, Any]:
    if not value or "@" not in value:
        return _err(field, value, "missing @")
    if not _EMAIL_RE.match(value):
        return _err(field, value, "invalid email format")
    local, domain = value.rsplit("@", 1)
    if not local or not domain or "." not in domain:
        return _err(field, value, "incomplete email")
    return {"field": field, "value": value, "ok": True}


def validate_url(value: str, field: str = "url") -> dict[str, Any]:
    if not value:
        return _err(field, value, "empty")
    if not _URL_RE.match(value):
        return _err(field, value, "invalid URL (expected http(s)://host)")
    return {"field": field, "value": value, "ok": True}


def validate_host(value: str, field: str = "host") -> dict[str, Any]:
    if not value:
        return _err(field, value, "empty")
    if _IP_RE.match(value) or _HOST_RE.match(value) or _DOMAIN_RE.match(value):
        return {"field": field, "value": value, "ok": True}
    return _err(field, value, "invalid hostname or IP")


def validate_port(value: str, field: str = "port") -> dict[str, Any]:
    if not value:
        return _err(field, value, "empty")
    if not _PORT_RE.match(value):
        return _err(field, value, "invalid port (1-65535)")
    p = int(value)
    if p < 1 or p > 65535:
        return _err(field, value, "out of range (1-65535)")
    return {"field": field, "value": value, "ok": True}


def validate_bool(value: str, field: str = "bool") -> dict[str, Any]:
    if not value:
        return _err(field, value, "empty")
    if not _BOOL_RE.match(value):
        return _err(field, value, "expected 0,1,true,false,yes,no,on,off")
    return {"field": field, "value": value, "ok": True}


_API_KEY_CHECKS: list[tuple[re.Pattern, str]] = [
    (_OPENAI_KEY_RE, "expected sk-... format"),
    (_GROQ_KEY_RE, "expected gsk-... format"),
    (_ANTHROPIC_KEY_RE, "expected sk-ant-... format"),
    (_HF_TOKEN_RE, "expected hf_... format"),
]


def validate_api_key(value: str, field: str = "api_key") -> dict[str, Any]:
    if not value:
        return _err(field, value, "empty")
    for pattern, error_msg in _API_KEY_CHECKS:
        if pattern.match(value):
            return {"field": field, "value": value[:6] + "...", "ok": True}
    # Generic fallback — any non-empty printable ASCII
    if re.match(r"^[\x21-\x7e]+$", value):
        return {"field": field, "value": value[:6] + "...", "ok": True}
    return _err(field, value, "unexpected characters")


# Mapping from key suffix/prefix to validator
_KEY_VALIDATORS: dict[str, Any] = {
    "_EMAIL": validate_email,
    "_USER": validate_email,
    "_HOST": validate_host,
    "_PORT": validate_port,
    "_URL": validate_url,
    "_TLS": validate_bool,
    "_TIMEOUT": validate_port,
    "_ENABLED": validate_bool,
    "_DISABLED": validate_bool,
    "_API_KEY": validate_api_key,
    "_API_TOKEN": validate_api_key,
    "_TOKEN": validate_api_key,
}


def validate_key_value(key: str, value: str) -> dict[str, Any] | None:
    """Pick validator by key suffix/prefix. Returns None when no validator applies."""
    upper = key.upper()
    for suffix, fn in _KEY_VALIDATORS.items():
        if upper.endswith(suffix) or upper.startswith(suffix.rstrip("_") + "_"):
            return fn(value, field=key)
    # Heuristic: key contains URL / HOST / EMAIL / PORT anywhere
    if "EMAIL" in upper:
        return validate_email(value, field=key)
    if "URL" in upper:
        return validate_url(value, field=key)
    if "HOST" in upper or "SERVER" in upper or "ADDRESS" in upper:
        return validate_host(value, field=key)
    if "PORT" in upper:
        return validate_port(value, field=key)
    return None
