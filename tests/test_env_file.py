from pathlib import Path

import pytest

from nlp2env.env_file import EnvFile, mask_value, resolve_env_path
from nlp2env.profiles import (
    api_profile_from_dict,
    api_profile_status,
    db_profile_from_dict,
    db_profile_status,
    email_profile_from_dict,
    email_profile_status,
)


def test_mask_secret():
    assert mask_value("SMTP_PASSWORD", "secret123") == "se***23"


def test_load_and_save_roundtrip(tmp_path: Path):
    path = tmp_path / ".env"
    path.write_text('SMTP_HOST=mail.example.com\nSMTP_PASSWORD="p@ss"\n', encoding="utf-8")
    env = EnvFile.load(path)
    assert env.get("SMTP_HOST") == "mail.example.com"
    assert env.get("SMTP_PASSWORD") == "p@ss"
    env.set_many({"SMTP_PORT": "587"})
    env.save(backup=False)
    reloaded = EnvFile.load(path)
    assert reloaded.get("SMTP_PORT") == "587"


def test_apply_text(tmp_path: Path):
    env = EnvFile(path=tmp_path / ".env")
    updates = env.apply_text("SMTP_HOST=smtp.gmail.com\nSMTP_PORT: 465")
    assert updates["SMTP_HOST"] == "smtp.gmail.com"
    assert updates["SMTP_PORT"] == "465"


def test_email_profile():
    data = email_profile_from_dict(
        {"host": "smtp.mail.com", "user": "a@b.c", "password": "x", "port": 587}
    )
    assert data["SMTP_HOST"] == "smtp.mail.com"
    assert data["SMTP_USER"] == "a@b.c"
    status = email_profile_status(data)
    assert status["configured"] is True
    assert status["missing"] == []


def test_email_profile_missing():
    status = email_profile_status({"SMTP_HOST": "x"})
    assert status["configured"] is False
    assert "SMTP_USER" in status["missing"]


def test_delete_key(tmp_path: Path):
    path = tmp_path / ".env"
    path.write_text("FOO=1\nBAR=2\n", encoding="utf-8")
    env = EnvFile.load(path)
    assert env.delete("FOO") is True
    assert env.delete("BAZ") is False
    assert env.get("FOO") is None
    assert env.get("BAR") == "2"


def test_api_profile():
    data = api_profile_from_dict({"openai": "sk-xxx", "groq": "gsk-yyy"})
    assert data["OPENAI_API_KEY"] == "sk-xxx"
    assert data["GROQ_API_KEY"] == "gsk-yyy"
    assert "ANTHROPIC_API_KEY" not in data
    status = api_profile_status(data)
    assert status["configured"] is True
    assert status["missing"] == ["ANTHROPIC_API_KEY", "HUGGINGFACE_API_TOKEN"]


def test_api_profile_empty():
    status = api_profile_status({})
    assert status["configured"] is False
    assert len(status["missing"]) == 4


def test_resolve_env_path_suffix(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("NLP2ENV_PROJECT_DIR", str(tmp_path))
    assert resolve_env_path(suffix="local") == tmp_path / ".env.local"
    assert resolve_env_path(suffix="production") == tmp_path / ".env.production"


def test_load_multi(tmp_path: Path):
    base = tmp_path / ".env"
    local = tmp_path / ".env.local"
    base.write_text("FOO=base\nBAR=1\n", encoding="utf-8")
    local.write_text("FOO=local\nBAZ=2\n", encoding="utf-8")
    env = EnvFile.load_multi(base, suffix="local")
    assert env.get("FOO") == "local"
    assert env.get("BAR") == "1"
    assert env.get("BAZ") == "2"


def test_db_profile():
    data = db_profile_from_dict(
        {"postgres_host": "db.example.com", "postgres_db": "mydb", "postgres_user": "admin", "postgres_password": "x"}
    )
    assert data["POSTGRES_HOST"] == "db.example.com"
    assert data["POSTGRES_PORT"] == "5432"
    status = db_profile_status(data)
    assert status["configured"] is True
    assert status["missing"] == []
    assert status["redis"] is False


def test_db_profile_missing():
    status = db_profile_status({"POSTGRES_HOST": "x"})
    assert status["configured"] is False
    assert "POSTGRES_DB" in status["missing"]
