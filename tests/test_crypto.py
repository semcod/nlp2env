"""Tests for crypto module."""

import os

import pytest

from nlp2env.crypto import (
    _derive_key,
    decrypt_value,
    encrypt_value,
    generate_key,
    mask_encrypted,
    rotate_encrypted_values,
)


@pytest.fixture(autouse=True)
def clear_env_key(monkeypatch):
    monkeypatch.delenv("NLP2ENV_MASTER_KEY", raising=False)


def test_generate_key():
    key = generate_key()
    assert len(key) == 44
    assert key.endswith("=")


def test_derive_key():
    key1 = _derive_key("my-password")
    key2 = _derive_key("my-password")
    assert key1 == key2
    assert len(key1) == 44


def test_encrypt_decrypt_roundtrip(monkeypatch, tmp_path):
    key = generate_key()
    monkeypatch.setenv("NLP2ENV_MASTER_KEY", key)
    plaintext = "secret123"
    encrypted = encrypt_value(plaintext)
    assert encrypted.startswith("enc:")
    decrypted = decrypt_value(encrypted)
    assert decrypted == plaintext


def test_decrypt_plaintext_passthrough():
    assert decrypt_value("plain-text") == "plain-text"
    assert decrypt_value("not-encrypted") == "not-encrypted"


def test_mask_encrypted():
    long_enc = "enc:abcdefghijklmnopqrstuvwxyz"
    masked = mask_encrypted(long_enc, visible=4)
    assert masked.startswith("enc:")
    assert "****" in masked
    assert masked.endswith("wxyz")


def test_mask_encrypted_short():
    short = "enc:abc"
    masked = mask_encrypted(short)
    assert masked == "enc:***"


def test_encrypt_without_key_raises():
    if os.getenv("NLP2ENV_MASTER_KEY"):
        pytest.skip("NLP2ENV_MASTER_KEY is set")
    with pytest.raises(RuntimeError, match="No encryption key"):
        encrypt_value("secret")


def test_rotate_encrypted_values(monkeypatch, tmp_path):
    old_key = generate_key()
    new_key = generate_key()
    monkeypatch.setenv("NLP2ENV_MASTER_KEY", old_key)
    encrypted = encrypt_value("secret")
    values = {"KEY": encrypted, "PLAIN": "visible"}
    rotated = rotate_encrypted_values(values, old_key.encode(), new_key.encode())
    assert rotated["PLAIN"] == "visible"
    assert rotated["KEY"].startswith("enc:")
    assert rotated["KEY"] != encrypted
    # Verify decryption with new key works
    monkeypatch.setenv("NLP2ENV_MASTER_KEY", new_key)
    decrypted = decrypt_value(rotated["KEY"])
    assert decrypted == "secret"
