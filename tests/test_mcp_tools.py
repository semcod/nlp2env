import json
from pathlib import Path

import pytest

pytest.importorskip("mcp")

from nlp2env_mcp.server import build_mcp


@pytest.fixture
def env_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    path = tmp_path / ".env"
    monkeypatch.setenv("NLP2ENV_ENV_FILE", str(path))
    return path


def test_interfaces():
    mcp = build_mcp()
    tools = {t.name: t for t in mcp._tool_manager.list_tools()}  # type: ignore[attr-defined]
    assert "nlp2env_set_email" in tools
    assert "nlp2env_interfaces" in tools
    assert "nlp2env_delete" in tools


def test_set_email_via_tool(env_path: Path):
    mcp = build_mcp()
    fn = mcp._tool_manager._tools["nlp2env_set_email"].fn  # type: ignore[attr-defined]
    out = json.loads(
        fn(
            host="smtp.example.com",
            user="jan@firma.pl",
            password="secret",
            port="587",
            tls="1",
            from_addr="jan@firma.pl",
        )
    )
    assert out["success"] is True
    assert env_path.is_file()
    text = env_path.read_text(encoding="utf-8")
    assert "SMTP_HOST=smtp.example.com" in text
    assert "SMTP_USER=jan@firma.pl" in text


def test_delete_via_tool(env_path: Path):
    mcp = build_mcp()
    env_path.write_text("FOO=1\nBAR=2\n", encoding="utf-8")
    fn = mcp._tool_manager._tools["nlp2env_delete"].fn  # type: ignore[attr-defined]
    out = json.loads(fn(keys="FOO,BAZ"))
    assert out["success"] is True
    assert out["removed"] == ["FOO"]
    assert out["missing"] == ["BAZ"]
    text = env_path.read_text(encoding="utf-8")
    assert "FOO=" not in text
    assert "BAR=2" in text
