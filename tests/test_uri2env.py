from pathlib import Path

import pytest

from uri2env.materialize import materialize_uri
from uri2env.uri import (
    is_env_uri,
    parse_env_uri,
    uri_for_env_file,
    uri_for_nlp2env_profile,
)


def test_env_uri_parse():
    uri = uri_for_nlp2env_profile("smtp", dest="/tmp/out/.env")
    assert is_env_uri(uri)
    parsed = parse_env_uri(uri)
    assert parsed["source"] == "nlp2env"
    assert parsed["parts"] == ["smtp"]
    assert parsed["dest"] == "/tmp/out/.env"


def test_materialize_file(tmp_path: Path):
    src = tmp_path / "source.env"
    src.write_text("FOO=bar\nBAZ=qux\n", encoding="utf-8")
    dest = tmp_path / "dest" / ".env"
    uri = uri_for_env_file(str(src), dest=str(dest))
    result = materialize_uri(uri)
    assert result.ok is True
    assert dest.is_file()
    assert "FOO=bar" in dest.read_text(encoding="utf-8")


def test_materialize_nlp2env_smtp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.test.example")
    monkeypatch.setenv("SMTP_USER", "user@test.example")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    dest = tmp_path / ".env"
    uri = uri_for_nlp2env_profile("smtp", dest=str(dest))
    result = materialize_uri(uri)
    assert result.ok is True
    text = dest.read_text(encoding="utf-8")
    assert "SMTP_HOST=smtp.test.example" in text
    assert "SMTP_USER=user@test.example" in text
