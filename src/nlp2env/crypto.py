"""Encryption for .env values using Fernet (AES-128-CBC + HMAC)."""

from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:
    Fernet = None  # type: ignore[misc,assignment]
    InvalidToken = Exception  # type: ignore[misc,assignment]


def _derive_key(password: str) -> bytes:
    """Derive 32-byte Fernet key from password using PBKDF2-like simple hash."""
    import hashlib
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), b"nlp2env_salt_v1", 100000, dklen=32)
    return base64.urlsafe_b64encode(derived)


def _load_master_key() -> bytes | None:
    """Load encryption key from env or ~/.nlp2env/key."""
    env_key = os.getenv("NLP2ENV_MASTER_KEY", "").strip()
    if env_key:
        if len(env_key) == 44 and env_key.endswith("="):
            return env_key.encode()
        return _derive_key(env_key)
    key_file = Path.home() / ".nlp2env" / "key"
    if key_file.is_file():
        return key_file.read_bytes().strip()
    return None


def encrypt_value(value: str, key: bytes | None = None) -> str:
    """Encrypt value, return 'enc:<base64>'. Returns plaintext if no key."""
    if not Fernet:
        raise RuntimeError("cryptography not installed; run: pip install cryptography")
    k = key or _load_master_key()
    if not k:
        raise RuntimeError("No encryption key; set NLP2ENV_MASTER_KEY or create ~/.nlp2env/key")
    f = Fernet(k)
    token = f.encrypt(value.encode("utf-8"))
    return f"enc:{token.decode('ascii')}"


def decrypt_value(value: str, key: bytes | None = None) -> str:
    """Decrypt 'enc:<base64>' or return plaintext if not encrypted."""
    if not isinstance(value, str) or not value.startswith("enc:"):
        return value
    if not Fernet:
        raise RuntimeError("cryptography not installed")
    k = key or _load_master_key()
    if not k:
        raise RuntimeError("No encryption key")
    f = Fernet(k)
    token = value[4:].encode("ascii")
    try:
        return f.decrypt(token).decode("utf-8")
    except InvalidToken as e:
        raise RuntimeError("Decryption failed: invalid key or corrupted data") from e


def generate_key() -> str:
    """Generate new Fernet key for user to save."""
    if not Fernet:
        raise RuntimeError("cryptography not installed")
    return Fernet.generate_key().decode("ascii")


def rotate_encrypted_values(values: dict[str, str], old_key: bytes, new_key: bytes) -> dict[str, str]:
    """Re-encrypt all 'enc:*' values with new key."""
    rotated: dict[str, str] = {}
    for k, v in values.items():
        if isinstance(v, str) and v.startswith("enc:"):
            plaintext = decrypt_value(v, key=old_key)
            rotated[k] = encrypt_value(plaintext, key=new_key)
        else:
            rotated[k] = v
    return rotated


def mask_encrypted(value: str, visible: int = 4) -> str:
    """Mask encrypted value for display: 'enc:****abcd'."""
    if not isinstance(value, str) or not value.startswith("enc:"):
        return value
    token = value[4:]
    if len(token) <= visible * 2:
        return f"enc:{'*' * len(token)}"
    return f"enc:{'*' * (len(token) - visible)}{token[-visible:]}"
