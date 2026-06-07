"""Parse, merge, and persist KEY=value .env files."""

from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SECRET_RE = re.compile(r"(password|secret|token|api_?key|private)", re.I)
_LINE_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")


def mask_value(key: str, value: str) -> str:
    if not value:
        return value
    if _SECRET_RE.search(key):
        return "***" if len(value) <= 8 else f"{value[:2]}***{value[-2:]}"
    return value


def resolve_env_path(path: str | Path | None = None) -> Path:
    if path:
        return Path(path).expanduser().resolve()
    env_file = os.getenv("NLP2ENV_ENV_FILE", "").strip()
    if env_file:
        return Path(env_file).expanduser().resolve()
    project = os.getenv("NLP2ENV_PROJECT_DIR", "").strip()
    if project:
        return (Path(project).expanduser() / ".env").resolve()
    return Path.cwd() / ".env"


@dataclass
class EnvFile:
    path: Path
    values: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path | None = None) -> EnvFile:
        resolved = resolve_env_path(path)
        values: dict[str, str] = {}
        if resolved.is_file():
            for raw in resolved.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                m = _LINE_RE.match(line)
                if not m:
                    continue
                key, val = m.group(1), m.group(2).strip()
                if (val.startswith('"') and val.endswith('"')) or (
                    val.startswith("'") and val.endswith("'")
                ):
                    val = val[1:-1]
                values[key] = val
        return cls(path=resolved, values=values)

    def get(self, key: str, default: str | None = None) -> str | None:
        return self.values.get(key, default)

    def set_many(self, updates: dict[str, str], *, overwrite: bool = True) -> dict[str, str]:
        changed: dict[str, str] = {}
        for key, value in updates.items():
            if not key or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
                raise ValueError(f"Invalid env key: {key!r}")
            if not overwrite and key in self.values:
                continue
            if self.values.get(key) != value:
                changed[key] = value
            self.values[key] = value
        return changed

    def delete(self, key: str) -> bool:
        if key in self.values:
            del self.values[key]
            return True
        return False

    def list_masked(self) -> dict[str, str]:
        return {k: mask_value(k, v) for k, v in sorted(self.values.items())}

    def backup(self, backup_dir: Path | None = None) -> Path | None:
        if not self.path.is_file():
            return None
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        dest_root = backup_dir or self.path.parent / ".nlp2env" / "backups"
        dest_root.mkdir(parents=True, exist_ok=True)
        dest = dest_root / f"{self.path.name}.{stamp}.bak"
        shutil.copy2(self.path, dest)
        return dest

    def save(self, *, backup: bool = True) -> dict[str, Any]:
        if backup and self.path.is_file():
            self.backup()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        for key in sorted(self.values):
            val = self.values[key]
            if re.search(r"[\s#\"']", val):
                val = '"' + val.replace("\\", "\\\\").replace('"', '\\"') + '"'
            lines.append(f"{key}={val}")
        content = "\n".join(lines) + ("\n" if lines else "")
        self.path.write_text(content, encoding="utf-8")
        return {"path": str(self.path), "keys": len(self.values)}

    def apply_text(self, text: str) -> dict[str, str]:
        """Parse KEY=value lines or simple 'key: value' pairs from text."""
        updates: dict[str, str] = {}
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                updates[key.strip()] = val.strip().strip('"').strip("'")
                continue
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip().upper().replace(" ", "_")
                if re.match(r"^[A-Z0-9_]+$", key):
                    updates[key] = val.strip().strip('"').strip("'")
        return updates
