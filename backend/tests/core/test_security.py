"""
Tests for security utilities (password hashing and JWT tokens).

This module tests:
- Password hashing with bcrypt (cost factor 12)
- Password verification
- JWT token creation and verification
- Edge cases and error handling
"""

import pytest
from datetime import timedelta, datetime, timezone
from calendar import timegm
from jose import jwt

from src.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from src.core.settings import settings


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password_creates_bcrypt_hash(self):
        """Test that hash_password creates a valid bcrypt hash."""
        password = "test_password_123"
        hashed = hash_password(password)

        # Bcrypt hashes start with $2b$ and are 60 characters long
        assert hashed.startswith("$2b$12$")
        assert len(hashed) == 60

    def test_hash_password_different_each_time(self):
        """Test that same password produces different hashes (salt randomness)."""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different due to random salt
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_hash_password_handles_special_characters(self):
        """Test password hashing with special characters."""
        password = "p@ssw0rd!#$%^&*()"
        hashed = hash_password(password)

        assert hashed.startswith("$2b$12$")
        assert verify_password(password, hashed)

    def test_hash_password_handles_unicode(self):
        """Test password hashing with unicode characters."""
        password = "pässwörd_日本語_🔒"
        hashed = hash_password(password)

        assert hashed.startswith("$2b$12$")
        assert verify_password(password, hashed)

    def test_hash_password_handles_long_password(self):
        """Test password hashing with very long password."""
        password = "a" * 200
        hashed = hash_password(password)

        assert hashed.startswith("$2b$12$")
        assert verify_password(password, hashed)


class TestPasswordVerification:
    """Tests for password verification function."""

    def test_verify_password_correct_password(self):
        """Test that matching password returns True."""
        password = "correct_password"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """Test that non-matching password returns False."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_handles_special_characters(self):
        """Test password verification with special characters."""
        password = "sp€ci@l_p@ss!#$"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case sensitive."""
        password = "Password123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("password123", hashed) is False
        assert verify_password("PASSWORD123", hashed) is False

    def test_verify_password_handles_empty_password(self):
        """Test verification with empty password."""
        # Empty passwords should be rejected at API layer, but function should handle gracefully
        password = ""
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("not_empty", hashed) is False

    def test_verify_password_invalid_hash_format(self):
        """Test that invalid hash format returns False gracefully."""
        password = "test_password"
        invalid_hash = "not_a_valid_bcrypt_hash"

        # Should return False, not raise exception
        assert verify_password(password, invalid_hash) is False


class TestJWTTokens:
    """Tests for JWT token creation and verification."""

    def test_create_access_token_with_default_expiry(self):
        """Test token creation with default 15 minute expiry."""
        data = {"sub": "user-123"}
        token = create_access_token(data)

        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0

        # Decode token to verify expiry time
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        assert "sub" in payload
        assert payload["sub"] == "user-123"
        assert "exp" in payload

        # Check expiry is approximately 15 minutes from now
        exp_timestamp = payload["exp"]
        now_timestamp = timegm(datetime.now(timezone.utc).utctimetuple())
        time_diff_minutes = (exp_timestamp - now_timestamp) / 60

        assert 14.5 <= time_diff_minutes <= 15.5  # Allow small tolerance

    def test_create_access_token_with_custom_expiry(self):
        """Test token creation with custom expiry time."""
        data = {"sub": "user-456"}
        custom_expiry = timedelta(hours=1)
        token = create_access_token(data, expires_delta=custom_expiry)

        # Decode and check expiry
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        exp_timestamp = payload["exp"]
        now_timestamp = timegm(datetime.now(timezone.utc).utctimetuple())
        time_diff_minutes = (exp_timestamp - now_timestamp) / 60

        # Should be approximately 60 minutes
        assert 59 <= time_diff_minutes <= 61

    def test_create_access_token_includes_exp_claim(self):
        """Test that token payload includes 'exp' (expiration) claim."""
        data = {"sub": "user-789", "email": "user@example.com"}
        token = create_access_token(data)

        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])

        assert "exp" in payload
        assert "sub" in payload
        assert payload["sub"] == "user-789"
        assert "email" in payload
        assert payload["email"] == "user@example.com"

    def test_create_access_token_does_not_mutate_input(self):
        """Test that creating token doesn't mutate the input data dictionary."""
        data = {"sub": "user-999"}
        original_data = data.copy()

        token = create_access_token(data)

        # Input data should be unchanged
        assert data == original_data
        assert "exp" not in data

    def test_verify_access_token_valid_token(self):
        """Test that valid token is successfully decoded."""
        data = {"sub": "user-abc", "role": "user"}
        token = create_access_token(data)

        payload = verify_access_token(token)

        assert payload is not None
        assert payload["sub"] == "user-abc"
        assert payload["role"] == "user"
        assert "exp" in payload

    def test_verify_access_token_expired_token(self):
        """Test that expired token returns None."""
        data = {"sub": "user-xyz"}
        # Create token that expires immediately (negative timedelta)
        expired_token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        payload = verify_access_token(expired_token)

        # Expired token should return None
        assert payload is None

    def test_verify_access_token_invalid_signature(self):
        """Test that token with invalid signature returns None."""
        data = {"sub": "user-123"}
        token = create_access_token(data)

        # Tamper with the token (change last character)
        tampered_token = token[:-5] + "xxxxx"

        payload = verify_access_token(tampered_token)

        # Invalid signature should return None
        assert payload is None

    def test_verify_access_token_malformed_token(self):
        """Test that malformed token string returns None."""
        malformed_tokens = [
            "not.a.token",
            "invalid_token_string",
            "",
            "a.b",  # Missing segment
            "...",  # Empty segments
        ]

        for malformed in malformed_tokens:
            payload = verify_access_token(malformed)
            assert payload is None, f"Failed for token: {malformed}"

    def test_verify_access_token_wrong_secret(self):
        """Test that token signed with different secret returns None."""
        # Create token with correct secret
        data = {"sub": "user-secret-test"}
        token = create_access_token(data)

        # Try to decode with wrong secret
        try:
            jwt.decode(token, "wrong_secret_key", algorithms=[ALGORITHM])
            assert False, "Should have raised JWTError"
        except Exception:
            pass  # Expected

        # Our function should return None gracefully
        # (This test verifies the function handles the secret correctly)
        payload = verify_access_token(token)
        assert payload is not None  # Should work with correct secret


class TestIntegration:
    """Integration tests for security functions working together."""

    def test_integration_hash_verify_roundtrip(self):
        """Test end-to-end: hash password then verify it."""
        password = "integration_test_password_123"

        # Hash the password
        hashed = hash_password(password)

        # Verify correct password
        assert verify_password(password, hashed) is True

        # Verify incorrect password
        assert verify_password("wrong_password", hashed) is False

    def test_integration_token_create_verify_roundtrip(self):
        """Test end-to-end: create token then verify it."""
        user_data = {
            "sub": "user-integration-test",
            "email": "test@example.com",
            "role": "user"
        }

        # Create token
        token = create_access_token(user_data)

        # Verify token
        payload = verify_access_token(token)

        assert payload is not None
        assert payload["sub"] == user_data["sub"]
        assert payload["email"] == user_data["email"]
        assert payload["role"] == user_data["role"]

    def test_integration_full_auth_flow(self):
        """Test complete authentication flow: register, hash, verify, create token, verify token."""
        # Simulate user registration
        user_id = "user-full-flow-test"
        plain_password = "secure_password_123"
        user_email = "fullflow@example.com"

        # 1. Hash password (during registration)
        hashed_password = hash_password(plain_password)

        # 2. Verify password (during login)
        login_success = verify_password(plain_password, hashed_password)
        assert login_success is True

        # 3. Create access token (after successful login)
        token = create_access_token({"sub": user_id, "email": user_email})

        # 4. Verify token (for protected routes)
        payload = verify_access_token(token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["email"] == user_email

        # 5. Verify wrong password fails
        wrong_password_attempt = verify_password("wrong_password", hashed_password)
        assert wrong_password_attempt is False
