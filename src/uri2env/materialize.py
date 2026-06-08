"""Materialize env:// URIs into .env files or dicts."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from nlp2env.env_file import EnvFile, resolve_env_path
from nlp2env.profiles import EMAIL_PROFILE_KEYS
from uri2env.uri import parse_env_uri


@dataclass
class MaterializeResult:
    ok: bool
    uri: str
    dest: str
    keys: list[str] = field(default_factory=list)
    source: str = ""
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "uri": self.uri,
            "dest": self.dest,
            "keys": self.keys,
            "source": self.source,
            "error": self.error,
        }


def _resolve_dest(params: dict[str, str], fallback: str | None = None) -> Path:
    dest = params.get("dest") or fallback or ""
    if dest:
        return Path(dest).expanduser().resolve()
    return resolve_env_path()


def _load_getv_profile(category: str, profile: str) -> dict[str, str]:
    try:
        from nlp2uri.systemmap.getv_load import load_profile_dict
    except ImportError as exc:
        raise RuntimeError("getv support requires nlp2uri[envmap] or getv on PATH") from exc
    return {k: str(v) for k, v in load_profile_dict(category, profile).items()}


def _materialize_getv(parts: list[str], dest: Path) -> MaterializeResult:
    if len(parts) < 2:
        raise ValueError("env://getv/{category}/{profile}[/{VAR}] required")
    category, profile = parts[0], parts[1]
    if len(parts) >= 3:
        var_name = parts[2]
        value = _load_getv_profile(category, profile).get(var_name)
        if value is None:
            raise ValueError(f"Brak zmiennej {var_name} w profilu getv {category}/{profile}")
        env = EnvFile.load(dest)
        env.set_many({var_name: value})
        env.save(backup=True)
        return MaterializeResult(
            ok=True,
            uri="",
            dest=str(dest),
            keys=[var_name],
            source=f"getv:{category}/{profile}",
        )

    values = _load_getv_profile(category, profile)
    env = EnvFile.load(dest)
    env.set_many(values)
    env.save(backup=True)
    return MaterializeResult(
        ok=True,
        uri="",
        dest=str(dest),
        keys=sorted(values.keys()),
        source=f"getv:{category}/{profile}",
    )


def _materialize_file(parts: list[str], dest: Path) -> MaterializeResult:
    if not parts:
        raise ValueError("env://file/{path} required")
    src = Path(parts[0]).expanduser().resolve()
    if not src.is_file():
        raise FileNotFoundError(f"Brak pliku źródłowego: {src}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    env = EnvFile.load(dest)
    return MaterializeResult(
        ok=True,
        uri="",
        dest=str(dest),
        keys=sorted(env.values.keys()),
        source=f"file:{src}",
    )


def _materialize_nlp2env(parts: list[str], dest: Path, params: dict[str, str]) -> MaterializeResult:
    profile = parts[0] if parts else "smtp"
    if profile not in {"smtp", "email"}:
        raise ValueError(f"Nieznany profil nlp2env: {profile}")

    env = EnvFile.load(dest)
    updates: dict[str, str] = {}
    for key in params:
        if key in {"dest", "action"}:
            continue
        if key in EMAIL_PROFILE_KEYS or key.startswith("SMTP_"):
            updates[key] = params[key]

    for key, val in os.environ.items():
        if key in EMAIL_PROFILE_KEYS and key not in updates and val.strip():
            updates[key] = val.strip()

    if not updates:
        raise ValueError(
            f"Brak wartości dla profilu {profile}. "
            "Ustaw zmienne SMTP_* w środowisku lub podaj ?SMTP_HOST=... w URI."
        )

    env.set_many(updates)
    env.save(backup=True)
    return MaterializeResult(
        ok=True,
        uri="",
        dest=str(dest),
        keys=sorted(updates.keys()),
        source=f"nlp2env:{profile}",
    )


def materialize_uri(uri: str, *, dest: str | None = None) -> MaterializeResult:
    """Resolve env:// URI and write merged keys to destination .env."""
    parsed = parse_env_uri(uri)
    target = _resolve_dest(parsed["params"], dest)
    source = parsed["source"]
    parts = parsed["parts"]

    try:
        if source == "getv":
            result = _materialize_getv(parts, target)
        elif source == "file":
            result = _materialize_file(parts, target)
        elif source == "nlp2env":
            result = _materialize_nlp2env(parts, target, parsed["params"])
        else:
            raise ValueError(f"Nieobsługiwane źródło env://: {source}")

        result.uri = uri
        return result
    except Exception as exc:
        return MaterializeResult(
            ok=False,
            uri=uri,
            dest=str(target),
            error=str(exc),
        )
