"""Compile env:// to OS actions (nlp2uri integration)."""

from __future__ import annotations

from typing import Any

from uri2env.uri import is_env_uri, parse_env_uri


def compile_env_uri(uri: str, host: Any) -> list[Any]:
    """Return OSAction list — uses nlp2env CLI hook when available."""
    if not is_env_uri(uri):
        raise ValueError(f"not an env uri: {uri}")

    parsed = parse_env_uri(uri)
    dest = parsed["params"].get("dest", ".env")

    try:
        from nlp2uri.models import OSAction
    except ImportError as exc:
        raise RuntimeError("compile_env_uri requires nlp2uri") from exc

    materializer = "uri2env"
    return [
        OSAction(
            host,
            materializer,
            ["materialize", "--uri", uri, "--dest", dest],
        )
    ]
