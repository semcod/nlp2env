from pathlib import Path

import pytest

from nlp2env.env_file import EnvFile, mask_value
from nlp2env.profiles import email_profile_from_dict, email_profile_status


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
