"""Tests for MFA/TOTP authentication module."""
import time
import pytest
from backend.app.services.auth_mfa import (
    generate_secret,
    generate_provisioning_uri,
    generate_recovery_codes,
    generate_totp,
    verify_totp,
    verify_recovery_code,
    hash_recovery_code,
    MFAService,
)


class TestTOTPGeneration:
    """Test TOTP secret and code generation."""

    def test_generate_secret_returns_base32(self):
        secret = generate_secret()
        assert len(secret) > 0
        # Base32 characters
        assert all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567' for c in secret)

    def test_generate_secret_unique(self):
        s1 = generate_secret()
        s2 = generate_secret()
        assert s1 != s2

    def test_generate_provisioning_uri(self):
        uri = generate_provisioning_uri("TESTSECRET", "user@example.com")
        assert uri.startswith("otpauth://totp/")
        assert "TESTSECRET" in uri
        assert "user%40example.com" in uri
        assert "NeuraReport" in uri

    def test_generate_totp_returns_digits(self):
        secret = generate_secret()
        code = generate_totp(secret)
        assert len(code) == 6
        assert code.isdigit()

    def test_generate_totp_deterministic(self):
        secret = generate_secret()
        ts = time.time()
        code1 = generate_totp(secret, ts)
        code2 = generate_totp(secret, ts)
        assert code1 == code2


class TestTOTPVerification:
    """Test TOTP code verification."""

    def test_verify_valid_code(self):
        secret = generate_secret()
        code = generate_totp(secret)
        assert verify_totp(secret, code)

    def test_verify_invalid_code(self):
        secret = generate_secret()
        assert not verify_totp(secret, "000000")

    def test_verify_empty_code(self):
        secret = generate_secret()
        assert not verify_totp(secret, "")
        assert not verify_totp(secret, None)

    def test_verify_with_window(self):
        secret = generate_secret()
        # Generate code for previous time step
        prev_ts = time.time() - 30
        prev_code = generate_totp(secret, prev_ts)
        # Should still validate with window=1
        assert verify_totp(secret, prev_code, window=1)


class TestRecoveryCodes:
    """Test recovery code generation and verification."""

    def test_generate_recovery_codes_count(self):
        codes = generate_recovery_codes(count=10)
        assert len(codes) == 10

    def test_generate_recovery_codes_unique(self):
        codes = generate_recovery_codes(count=10)
        assert len(set(codes)) == 10

    def test_generate_recovery_codes_format(self):
        codes = generate_recovery_codes()
        for code in codes:
            assert "-" in code
            assert len(code) == 9  # XXXX-XXXX

    def test_verify_recovery_code_valid(self):
        codes = generate_recovery_codes()
        valid, used = verify_recovery_code(codes[0], codes)
        assert valid
        assert used == codes[0]

    def test_verify_recovery_code_invalid(self):
        codes = generate_recovery_codes()
        valid, used = verify_recovery_code("INVALID-CODE", codes)
        assert not valid
        assert used is None

    def test_verify_recovery_code_case_insensitive(self):
        codes = generate_recovery_codes()
        lower_code = codes[0].lower()
        valid, _ = verify_recovery_code(lower_code, codes)
        assert valid

    def test_hash_recovery_code(self):
        code = "ABCD-1234"
        hashed = hash_recovery_code(code)
        assert len(hashed) == 64  # SHA-256 hex digest


class TestMFAService:
    """Test the MFA service facade."""

    def test_enroll(self):
        service = MFAService()
        enrollment = service.enroll("user_1", "user@test.com")
        assert enrollment.secret
        assert enrollment.provisioning_uri.startswith("otpauth://")
        assert len(enrollment.recovery_codes) == 10

    def test_verify_totp(self):
        service = MFAService()
        enrollment = service.enroll("user_2", "user2@test.com")
        code = generate_totp(enrollment.secret)
        result = service.verify(enrollment.secret, code)
        assert result.valid
        assert result.method == "totp"

    def test_verify_recovery(self):
        service = MFAService()
        enrollment = service.enroll("user_3", "user3@test.com")
        result = service.verify(enrollment.secret, enrollment.recovery_codes[0], enrollment.recovery_codes)
        assert result.valid
        assert result.method == "recovery"
        assert result.recovery_code_used == enrollment.recovery_codes[0]

    def test_verify_invalid(self):
        service = MFAService()
        enrollment = service.enroll("user_4", "user4@test.com")
        result = service.verify(enrollment.secret, "000000")
        assert not result.valid

    def test_regenerate_recovery_codes(self):
        service = MFAService()
        codes = service.regenerate_recovery_codes("user_5")
        assert len(codes) == 10
