"""Parse nlp2env e2e scenarios from TestTOON (*.testql.toon.yaml).

Uses the TestQL tabular TOON format (testql), not DOQL. DOQL declares *what*
to build; TestTOON declares *how* to test NL → .env flows.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_HEADER_RE = re.compile(r"^([A-Z_]+)(?:\[(\d+)\])?\{([^}]*)\}:\s*$")
_META_RE = re.compile(r"^#\s*([A-Z_]+):\s*(.+)$")


@dataclass
class ToonSection:
    name: str
    columns: list[str]
    rows: list[list[str]] = field(default_factory=list)


@dataclass
class ToonScript:
    meta: dict[str, str] = field(default_factory=dict)
    sections: dict[str, ToonSection] = field(default_factory=dict)


@dataclass
class PromptScenario:
    prompt_id: str
    fields: dict[str, str] = field(default_factory=dict)
    expects: list[str] = field(default_factory=list)

    @property
    def nl(self) -> str:
        return self.fields.get("nl", "")

    @property
    def source(self) -> str:
        return self.fields.get("source", "inline").lower()

    @property
    def tool(self) -> str:
        return self.fields.get("tool", "")

    @property
    def after(self) -> str:
        return self.fields.get("after", "")

    @property
    def assert_configured(self) -> bool:
        return self.fields.get("assert_configured", "").lower() in {"1", "true", "yes"}

    def inline_arguments(self) -> dict[str, str]:
        skip = {"nl", "source", "tool", "after", "assert_configured", "lang", "id"}
        return {k: v for k, v in self.fields.items() if k not in skip and v}


def _strip_quoted(line: str) -> str:
    out: list[str] = []
    in_quote: str | None = None
    prev = ""
    for ch in line:
        if in_quote:
            if ch == in_quote and prev != "\\":
                in_quote = None
            prev = ch
            continue
        if ch in ('"', "'"):
            in_quote = ch
            prev = ch
            continue
        out.append(ch)
        prev = ch
    return "".join(out)


def _detect_sep(line: str) -> str:
    return "|" if "|" in _strip_quoted(line) else ","


def _split_row(line: str, sep: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    in_quote: str | None = None
    prev = ""
    for ch in line:
        if in_quote:
            buf.append(ch)
            if ch == in_quote and prev != "\\":
                in_quote = None
            prev = ch
            continue
        if ch in ('"', "'"):
            in_quote = ch
            buf.append(ch)
            prev = ch
            continue
        if ch == sep:
            parts.append("".join(buf))
            buf = []
            prev = ch
            continue
        buf.append(ch)
        prev = ch
    parts.append("".join(buf))
    return parts


def _parse_value(raw: str) -> str:
    val = raw.strip()
    if val == "-":
        return ""
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1].replace('\\"', '"').replace("\\'", "'")
    return val


def parse_testtoon(text: str) -> ToonScript:
    script = ToonScript()
    current: ToonSection | None = None
    sep = ","

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        meta = _META_RE.match(stripped)
        if meta:
            script.meta[meta.group(1).lower()] = meta.group(2).strip()
            continue
        if stripped.startswith("#"):
            continue
        header = _HEADER_RE.match(stripped)
        if header:
            name = header.group(1)
            cols = [c.strip() for c in header.group(3).split(",") if c.strip()]
            current = ToonSection(name=name, columns=cols)
            script.sections[name] = current
            sep = ","
            continue
        if current is None:
            continue
        sep = _detect_sep(stripped)
        cells = [_parse_value(c) for c in _split_row(stripped, sep)]
        while len(cells) < len(current.columns):
            cells.append("")
        current.rows.append(cells[: len(current.columns)])

    return script


def scenarios_from_toon(script: ToonScript) -> list[PromptScenario]:
    prompts = script.sections.get("PROMPTS")
    if not prompts:
        raise ValueError("Brak sekcji PROMPTS w pliku TestTOON")

    col_index = {name: idx for idx, name in enumerate(prompts.columns)}
    required = {"id"}
    if not required.issubset(col_index):
        raise ValueError(f"PROMPTS wymaga kolumn: {sorted(required)}")

    fields_section = script.sections.get("PROMPT_FIELDS")
    assert_section = script.sections.get("ASSERT_ENV")

    extra_fields: dict[str, dict[str, str]] = {}
    if fields_section:
        fcols = {name: idx for idx, name in enumerate(fields_section.columns)}
        for row in fields_section.rows:
            pid = row[fcols["prompt_id"]]
            extra_fields.setdefault(pid, {})[row[fcols["key"]]] = row[fcols["value"]]

    expects: dict[str, list[str]] = {}
    if assert_section:
        acols = {name: idx for idx, name in enumerate(assert_section.columns)}
        for row in assert_section.rows:
            pid = row[acols["prompt_id"]]
            expects.setdefault(pid, []).append(row[acols["expect"]])

    scenarios: list[PromptScenario] = []
    for row in prompts.rows:
        pid = row[col_index["id"]]
        fields: dict[str, str] = {}
        for col, idx in col_index.items():
            if col == "id":
                continue
            val = row[idx]
            if val:
                fields[col] = val
        fields.update(extra_fields.get(pid, {}))
        scenarios.append(
            PromptScenario(prompt_id=pid, fields=fields, expects=expects.get(pid, []))
        )
    return scenarios


def load_scenarios(path: Path | str) -> list[PromptScenario]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    return scenarios_from_toon(parse_testtoon(text))
