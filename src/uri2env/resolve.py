"""NL hints → env:// URI (for nlp2uri resolve layer)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from uri2env.uri import uri_for_getv_profile, uri_for_nlp2env_profile


@dataclass(frozen=True)
class ResolvedEnvUri:
    uri: str
    confidence: float
    match_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "uri": self.uri,
            "confidence": self.confidence,
            "match_reason": self.match_reason,
        }


def resolve_prompt_to_env_uri(prompt: str, *, dest: str | None = None) -> list[ResolvedEnvUri]:
    """Map NL text to env:// URIs (materialize getv profile or nlp2env SMTP)."""
    normalized = re.sub(r"\s+", " ", prompt.lower().strip())
    if not normalized:
        return []

    hits: list[ResolvedEnvUri] = []

    smtp_hints = ("smtp", "poczt", "mail", "email", "skrzynk", "outgoing")
    if any(h in normalized for h in smtp_hints):
        hits.append(
            ResolvedEnvUri(
                uri=uri_for_nlp2env_profile("smtp", dest=dest),
                confidence=0.82,
                match_reason="nlp2env:smtp_profile",
            )
        )

    sync_hints = ("sync", "zsynchroniz", "materializ", "export", "skopiuj", "copy")
    env_hints = (".env", "env", "zmienne", "variables", "getv")
    if any(h in normalized for h in sync_hints) and any(h in normalized for h in env_hints):
        hits.append(
            ResolvedEnvUri(
                uri=uri_for_getv_profile("llm", "default", dest=dest or ".env"),
                confidence=0.75,
                match_reason="getv:default_profile",
            )
        )

    try:
        from nlp2uri.systemmap.getv_uri import resolve_prompt_against_getv

        for item in resolve_prompt_against_getv(prompt, max_results=3):
            category = item.entry_name or "llm"
            profile_uri = uri_for_getv_profile(category.split("/")[0], category.split("/")[-1], dest=dest)
            hits.append(
                ResolvedEnvUri(
                    uri=profile_uri,
                    confidence=min(item.confidence, 0.9),
                    match_reason=f"getv:{item.match_reason}",
                )
            )
    except ImportError:
        pass

    seen: set[str] = set()
    unique: list[ResolvedEnvUri] = []
    for hit in sorted(hits, key=lambda h: h.confidence, reverse=True):
        if hit.uri in seen:
            continue
        seen.add(hit.uri)
        unique.append(hit)
    return unique
