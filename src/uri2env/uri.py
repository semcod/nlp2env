"""env:// URI builders and parsing."""

from __future__ import annotations

from urllib.parse import quote, unquote, urlparse

ENV_SCHEME = "env"
_GETV_SOURCE = "getv"
_FILE_SOURCE = "file"
_NLP2ENV_SOURCE = "nlp2env"


def _encode(value: str) -> str:
    return quote(value, safe="")


def _decode(value: str) -> str:
    return unquote(value or "")


def uri_for_getv_profile(category: str, profile: str, *, dest: str | None = None) -> str:
    uri = f"{ENV_SCHEME}://{_GETV_SOURCE}/{_encode(category)}/{_encode(profile)}"
    if dest:
        uri += f"?dest={_encode(dest)}"
    return uri


def uri_for_getv_var(category: str, profile: str, var_name: str, *, dest: str | None = None) -> str:
    uri = (
        f"{ENV_SCHEME}://{_GETV_SOURCE}/{_encode(category)}/"
        f"{_encode(profile)}/{_encode(var_name)}"
    )
    if dest:
        uri += f"?dest={_encode(dest)}"
    return uri


def uri_for_env_file(path: str, *, dest: str | None = None) -> str:
    uri = f"{ENV_SCHEME}://{_FILE_SOURCE}/{_encode(path)}"
    if dest:
        uri += f"?dest={_encode(dest)}"
    return uri


def uri_for_nlp2env_profile(profile: str, *, dest: str | None = None) -> str:
    uri = f"{ENV_SCHEME}://{_NLP2ENV_SOURCE}/{_encode(profile)}"
    if dest:
        uri += f"?dest={_encode(dest)}"
    return uri


def is_env_uri(uri: str) -> bool:
    return urlparse(uri).scheme.lower() == ENV_SCHEME


def parse_env_uri(uri: str) -> dict[str, str]:
    if not is_env_uri(uri):
        raise ValueError(f"not an env uri: {uri}")
    parsed = urlparse(uri)
    source = _decode(parsed.netloc)
    parts = [_decode(p) for p in parsed.path.split("/") if p]
    params = {}
    if parsed.query:
        for chunk in parsed.query.split("&"):
            if "=" in chunk:
                k, v = chunk.split("=", 1)
                params[k] = _decode(v)
    return {
        "source": source,
        "parts": parts,
        "params": params,
        "dest": params.get("dest", ""),
        "action": params.get("action", "materialize"),
    }


def build_env_uri_index() -> dict[str, dict[str, str]]:
    """Minimal index for nlp2uri — known nlp2env profile URIs."""
    profiles = ("smtp", "email")
    entries: dict[str, dict[str, str]] = {}
    for profile in profiles:
        uri = uri_for_nlp2env_profile(profile)
        entries[uri] = {
            "kind": "nlp2env_profile",
            "profile": profile,
            "description": f"Materialize nlp2env {profile} profile keys to .env",
        }
    return entries
