"""
Multi-Factor Authentication (MFA) service using TOTP.

Provides:
- TOTP secret generation and QR code URLs
- TOTP code verification
- Recovery codes generation and validation
- MFA enrollment and management

Based on: pyauth/pyotp + RFC 6238 (TOTP) patterns.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

logger = logging.getLogger("neura.auth.mfa")

# ---------------------------------------------------------------------------
# TOTP parameters (RFC 6238 compliant)
# ---------------------------------------------------------------------------
TOTP_DIGITS = 6
TOTP_PERIOD = 30  # seconds
TOTP_ALGORITHM = "sha1"
TOTP_ISSUER = "NeuraReport"
RECOVERY_CODE_COUNT = 10
RECOVERY_CODE_LENGTH = 8


@dataclass
class MFAEnrollment:
    """MFA enrollment result."""
    secret: str
    provisioning_uri: str
    recovery_codes: list[str]


@dataclass
class MFAVerification:
    """MFA verification result."""
    valid: bool
    method: str  # "totp" or "recovery"
    recovery_code_used: Optional[str] = None


def generate_secret(length: int = 32) -> str:
    """Generate a base32-encoded TOTP secret."""
    # Generate random bytes and encode to base32
    random_bytes = secrets.token_bytes(length)
    import base64
    return base64.b32encode(random_bytes).decode("ascii").rstrip("=")


def generate_provisioning_uri(secret: str, user_email: str, issuer: str = TOTP_ISSUER) -> str:
    """Generate an otpauth:// URI for QR code scanning."""
    label = quote(f"{issuer}:{user_email}", safe="")
    params = (
        f"secret={secret}"
        f"&issuer={quote(issuer)}"
        f"&algorithm={TOTP_ALGORITHM.upper()}"
        f"&digits={TOTP_DIGITS}"
        f"&period={TOTP_PERIOD}"
    )
    return f"otpauth://totp/{label}?{params}"


def generate_recovery_codes(count: int = RECOVERY_CODE_COUNT, length: int = RECOVERY_CODE_LENGTH) -> list[str]:
    """Generate a set of recovery codes."""
    codes = []
    for _ in range(count):
        code = secrets.token_hex(length // 2).upper()
        # Format as XXXX-XXXX for readability
        formatted = f"{code[:4]}-{code[4:]}"
        codes.append(formatted)
    return codes


def _hotp(secret_bytes: bytes, counter: int) -> str:
    """Generate an HOTP value (RFC 4226)."""
    counter_bytes = counter.to_bytes(8, byteorder="big")
    mac = hmac.new(secret_bytes, counter_bytes, hashlib.sha1).digest()

    # Dynamic truncation
    offset = mac[-1] & 0x0F
    truncated = (
        ((mac[offset] & 0x7F) << 24)
        | ((mac[offset + 1] & 0xFF) << 16)
        | ((mac[offset + 2] & 0xFF) << 8)
        | (mac[offset + 3] & 0xFF)
    )

    code = truncated % (10 ** TOTP_DIGITS)
    return str(code).zfill(TOTP_DIGITS)


def _decode_secret(secret: str) -> bytes:
    """Decode a base32 secret to bytes."""
    import base64
    # Pad the secret to a multiple of 8
    padding = (8 - len(secret) % 8) % 8
    padded = secret + "=" * padding
    return base64.b32decode(padded.upper())


def generate_totp(secret: str, timestamp: Optional[float] = None) -> str:
    """Generate a TOTP code for the current time step."""
    ts = timestamp or time.time()
    counter = int(ts) // TOTP_PERIOD
    secret_bytes = _decode_secret(secret)
    return _hotp(secret_bytes, counter)


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    """
    Verify a TOTP code against the secret.

    Allows a window of +/- `window` time steps to account for clock skew.
    """
    if not code or not secret:
        return False

    # Normalize code
    code = code.strip().replace(" ", "").replace("-", "")
    if len(code) != TOTP_DIGITS:
        return False

    current_time = time.time()
    current_counter = int(current_time) // TOTP_PERIOD

    for offset in range(-window, window + 1):
        expected = generate_totp(secret, (current_counter + offset) * TOTP_PERIOD)
        if hmac.compare_digest(code, expected):
            return True

    return False


def verify_recovery_code(code: str, stored_codes: list[str]) -> tuple[bool, Optional[str]]:
    """
    Verify a recovery code against stored codes.

    Returns (is_valid, code_used). The caller should remove the used code.
    """
    normalized = code.strip().upper().replace(" ", "")

    for stored in stored_codes:
        stored_normalized = stored.strip().upper().replace(" ", "")
        if hmac.compare_digest(normalized, stored_normalized):
            return True, stored

    return False, None


def hash_recovery_code(code: str) -> str:
    """Hash a recovery code for secure storage."""
    normalized = code.strip().upper().replace(" ", "")
    return hashlib.sha256(normalized.encode()).hexdigest()


class MFAService:
    """
    MFA management service.

    Coordinates TOTP enrollment, verification, and recovery code management.
    Stores MFA secrets and recovery codes in the user database.
    """

    def __init__(self):
        self._logger = logging.getLogger("neura.auth.mfa.service")

    def enroll(self, user_id: str, user_email: str) -> MFAEnrollment:
        """
        Begin MFA enrollment for a user.

        Returns the secret, provisioning URI, and recovery codes.
        The caller must store these and require verification before activation.
        """
        secret = generate_secret()
        uri = generate_provisioning_uri(secret, user_email)
        recovery_codes = generate_recovery_codes()

        self._logger.info(
            "mfa_enrollment_started",
            extra={"event": "mfa_enrollment_started", "user_id": user_id},
        )

        return MFAEnrollment(
            secret=secret,
            provisioning_uri=uri,
            recovery_codes=recovery_codes,
        )

    def verify(self, secret: str, code: str, recovery_codes: Optional[list[str]] = None) -> MFAVerification:
        """
        Verify an MFA code (TOTP or recovery).

        Tries TOTP first, then falls back to recovery codes.
        """
        # Try TOTP
        if verify_totp(secret, code):
            return MFAVerification(valid=True, method="totp")

        # Try recovery code
        if recovery_codes:
            valid, used_code = verify_recovery_code(code, recovery_codes)
            if valid:
                self._logger.info(
                    "mfa_recovery_code_used",
                    extra={"event": "mfa_recovery_code_used"},
                )
                return MFAVerification(valid=True, method="recovery", recovery_code_used=used_code)

        return MFAVerification(valid=False, method="none")

    def regenerate_recovery_codes(self, user_id: str) -> list[str]:
        """Generate a new set of recovery codes (invalidates old ones)."""
        codes = generate_recovery_codes()
        self._logger.info(
            "mfa_recovery_codes_regenerated",
            extra={"event": "mfa_recovery_codes_regenerated", "user_id": user_id},
        )
        return codes


def get_mfa_service() -> MFAService:
    return MFAService()
