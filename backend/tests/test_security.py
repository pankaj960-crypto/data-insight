"""Tests for security utilities."""

from app.utils.security import create_access_token, decode_token, get_password_hash, verify_password


def test_password_hashing():
    hashed = get_password_hash("TestPassword123")
    assert verify_password("TestPassword123", hashed)
    assert not verify_password("WrongPassword", hashed)


def test_jwt_tokens():
    token = create_access_token({"sub": "1"})
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["type"] == "access"
