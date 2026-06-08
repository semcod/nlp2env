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
    assert "nlp2env_set_api" in tools
    assert "nlp2env_api_status" in tools
    assert "nlp2env_set_db" in tools
    assert "nlp2env_db_status" in tools
    assert "nlp2env_generate_key" in tools
    assert "nlp2env_encrypt" in tools
    assert "nlp2env_decrypt" in tools
    assert "nlp2env_load_multi" in tools
    assert "nlp2env_list_files" in tools
    assert "nlp2env_migrate" in tools


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


def test_set_email_rejects_invalid_host(env_path: Path):
    mcp = build_mcp()
    fn = mcp._tool_manager._tools["nlp2env_set_email"].fn  # type: ignore[attr-defined]
    out = json.loads(fn(host="not a host", user="jan@firma.pl", password="x"))
    assert out["success"] is False
    assert "SMTP_HOST" in out["error"]


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


def test_set_api_via_tool(env_path: Path):
    mcp = build_mcp()
    fn = mcp._tool_manager._tools["nlp2env_set_api"].fn  # type: ignore[attr-defined]
    out = json.loads(fn(openai_api_key="sk-test", groq_api_key="gsk-test"))
    assert out["success"] is True
    assert out["api_status"]["configured"] is True
    assert "OPENAI_API_KEY" in out["changed"]
    text = env_path.read_text(encoding="utf-8")
    assert "OPENAI_API_KEY=sk-test" in text
    assert "GROQ_API_KEY=gsk-test" in text


def test_api_status_via_tool(env_path: Path):
    env_path.write_text("OPENAI_API_KEY=sk-old\n", encoding="utf-8")
    mcp = build_mcp()
    fn = mcp._tool_manager._tools["nlp2env_api_status"].fn  # type: ignore[attr-defined]
    out = json.loads(fn())
    assert out["success"] is True
    assert out["api_status"]["configured"] is True
    assert out["api_status"]["missing"] == ["ANTHROPIC_API_KEY", "GROQ_API_KEY", "HUGGINGFACE_API_TOKEN"]


def test_load_multi_via_tool(env_path: Path, tmp_path: Path):
    local = tmp_path / ".env.local"
    local.write_text("SMTP_HOST=localhost\nSMTP_PORT=2525\n", encoding="utf-8")
    mcp = build_mcp()
    fn = mcp._tool_manager._tools["nlp2env_load_multi"].fn  # type: ignore[attr-defined]
    out = json.loads(fn(suffix="local", env_file=str(env_path)))
    assert out["success"] is True
    assert ".env.local" in str(out["sources"][-1])


def test_set_db_via_tool(env_path: Path):
    mcp = build_mcp()
    fn = mcp._tool_manager._tools["nlp2env_set_db"].fn  # type: ignore[attr-defined]
    out = json.loads(
        fn(
            postgres_host="db.example.com",
            postgres_db="mydb",
            postgres_user="admin",
            postgres_password="secret",
            redis_host="localhost",
        )
    )
    assert out["success"] is True
    assert out["db_status"]["configured"] is True
    text = env_path.read_text(encoding="utf-8")
    assert "POSTGRES_HOST=db.example.com" in text
    assert "REDIS_HOST=localhost" in text


def test_db_status_via_tool(env_path: Path):
    env_path.write_text("POSTGRES_HOST=x\nPOSTGRES_DB=y\nPOSTGRES_USER=z\nPOSTGRES_PASSWORD=w\n", encoding="utf-8")
    mcp = build_mcp()
    fn = mcp._tool_manager._tools["nlp2env_db_status"].fn  # type: ignore[attr-defined]
    out = json.loads(fn())
    assert out["success"] is True
    assert out["db_status"]["configured"] is True
    assert out["db_status"]["redis"] is False


def test_list_files_via_tool(env_path: Path):
    env_path.write_text("FOO=1\n", encoding="utf-8")
    mcp = build_mcp()
    fn = mcp._tool_manager._tools["nlp2env_list_files"].fn  # type: ignore[attr-defined]
    out = json.loads(fn(project_dir=str(env_path.parent)))
    assert out["success"] is True
    assert any(".env" in f for f in out["files"])


def test_generate_key_via_tool(monkeypatch):
    monkeypatch.setenv("NLP2ENV_MASTER_KEY", "")
    mcp = build_mcp()
    fn = mcp._tool_manager._tools["nlp2env_generate_key"].fn  # type: ignore[attr-defined]
    out = json.loads(fn())
    assert out["success"] is True
    assert "key" in out
    assert out["key"].endswith("=")


def test_encrypt_decrypt_via_tool(monkeypatch):
    from nlp2env.crypto import generate_key

    key = generate_key()
    monkeypatch.setenv("NLP2ENV_MASTER_KEY", key)
    mcp = build_mcp()
    encrypt_fn = mcp._tool_manager._tools["nlp2env_encrypt"].fn  # type: ignore[attr-defined]
    decrypt_fn = mcp._tool_manager._tools["nlp2env_decrypt"].fn  # type: ignore[attr-defined]

    enc_out = json.loads(encrypt_fn(plaintext="my-secret"))
    assert enc_out["success"] is True
    assert enc_out["encrypted"].startswith("enc:")

    dec_out = json.loads(decrypt_fn(ciphertext=enc_out["encrypted"]))
    assert dec_out["success"] is True
    assert dec_out["decrypted"] == "my-secret"


def test_migrate_via_tool(tmp_path: Path):
    base = tmp_path / ".env"
    local = tmp_path / ".env.local"
    base.write_text("FOO_SECRET=base_value\nBAR=shared\n", encoding="utf-8")
    mcp = build_mcp()
    fn = mcp._tool_manager._tools["nlp2env_migrate"].fn  # type: ignore[attr-defined]
    out = json.loads(
        fn(keys="FOO_SECRET,BAR", target_suffix="local", env_file=str(base), remove_from_source=False)
    )
    assert out["success"] is True
    assert out["migrated"]["FOO_SECRET"] == "ba***ue"
    assert local.is_file()
    local_text = local.read_text(encoding="utf-8")
    assert "FOO_SECRET=base_value" in local_text
    base_text = base.read_text(encoding="utf-8")
    assert "FOO_SECRET=base_value" in base_text  # not removed
