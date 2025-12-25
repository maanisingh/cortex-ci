"""
MFA/TOTP Authentication Module (Phase 3)
Implements Time-based One-Time Password (TOTP) authentication.
"""

import secrets
import base64
from typing import List, Optional
from datetime import datetime
import hashlib
import hmac
import struct
import time

import structlog

from app.core.config import settings

logger = structlog.get_logger()


class TOTPGenerator:
    """
    RFC 6238 compliant TOTP generator.
    Generates and verifies time-based one-time passwords.
    """

    def __init__(
        self,
        secret: str,
        digits: int = 6,
        interval: int = 30,
        algorithm: str = "sha1",
    ):
        self.secret = secret
        self.digits = digits
        self.interval = interval
        self.algorithm = algorithm

    def _decode_secret(self) -> bytes:
        """Decode base32 secret to bytes."""
        # Add padding if necessary
        padded = self.secret + "=" * ((8 - len(self.secret) % 8) % 8)
        return base64.b32decode(padded.upper())

    def _get_counter(self, timestamp: Optional[float] = None) -> int:
        """Get current counter value based on time."""
        if timestamp is None:
            timestamp = time.time()
        return int(timestamp // self.interval)

    def _generate_hotp(self, counter: int) -> str:
        """Generate HOTP value for given counter."""
        key = self._decode_secret()
        counter_bytes = struct.pack(">Q", counter)

        # HMAC-SHA1
        if self.algorithm == "sha1":
            hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        elif self.algorithm == "sha256":
            hmac_hash = hmac.new(key, counter_bytes, hashlib.sha256).digest()
        elif self.algorithm == "sha512":
            hmac_hash = hmac.new(key, counter_bytes, hashlib.sha512).digest()
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")

        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        binary = struct.unpack(">I", hmac_hash[offset : offset + 4])[0] & 0x7FFFFFFF

        # Generate OTP
        otp = binary % (10**self.digits)
        return str(otp).zfill(self.digits)

    def generate(self, timestamp: Optional[float] = None) -> str:
        """Generate current TOTP value."""
        counter = self._get_counter(timestamp)
        return self._generate_hotp(counter)

    def verify(self, code: str, window: int = 1, timestamp: Optional[float] = None) -> bool:
        """
        Verify TOTP code with time window tolerance.

        Args:
            code: The TOTP code to verify
            window: Number of intervals to check before/after current time
            timestamp: Optional timestamp (defaults to current time)
        """
        if len(code) != self.digits:
            return False

        counter = self._get_counter(timestamp)

        # Check current and adjacent windows
        for offset in range(-window, window + 1):
            expected = self._generate_hotp(counter + offset)
            if hmac.compare_digest(code, expected):
                return True

        return False


def generate_secret(length: int = 32) -> str:
    """
    Generate a cryptographically secure random secret.

    Args:
        length: Number of bytes for the secret (default 32 = 256 bits)

    Returns:
        Base32 encoded secret string
    """
    random_bytes = secrets.token_bytes(length)
    return base64.b32encode(random_bytes).decode("utf-8").rstrip("=")


def generate_backup_codes(count: int = 10) -> List[str]:
    """
    Generate backup codes for MFA recovery.

    Args:
        count: Number of backup codes to generate

    Returns:
        List of backup code strings
    """
    codes = []
    for _ in range(count):
        # Generate 8-character alphanumeric codes
        code = secrets.token_hex(4).upper()
        codes.append(code)
    return codes


def hash_backup_code(code: str) -> str:
    """
    Hash a backup code for secure storage.

    Args:
        code: The backup code to hash

    Returns:
        SHA-256 hash of the code
    """
    return hashlib.sha256(code.encode()).hexdigest()


def verify_backup_code(code: str, hashed_codes: List[str]) -> Optional[int]:
    """
    Verify a backup code against stored hashes.

    Args:
        code: The backup code to verify
        hashed_codes: List of hashed backup codes

    Returns:
        Index of matching code if found, None otherwise
    """
    code_hash = hash_backup_code(code.upper().replace("-", ""))
    for idx, stored_hash in enumerate(hashed_codes):
        if hmac.compare_digest(code_hash, stored_hash):
            return idx
    return None


def generate_provisioning_uri(
    secret: str,
    email: str,
    issuer: Optional[str] = None,
) -> str:
    """
    Generate otpauth:// URI for QR code generation.

    Args:
        secret: The TOTP secret
        email: User's email address
        issuer: Application name (default from settings)

    Returns:
        otpauth:// URI string
    """
    issuer = issuer or settings.MFA_ISSUER

    # URL encode the parameters
    from urllib.parse import quote

    label = quote(f"{issuer}:{email}")
    params = f"secret={secret}&issuer={quote(issuer)}&algorithm=SHA1&digits=6&period=30"

    return f"otpauth://totp/{label}?{params}"


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    """
    Verify a TOTP code.

    Args:
        secret: The user's TOTP secret
        code: The 6-digit code to verify
        window: Time window tolerance (default 1 = ±30 seconds)

    Returns:
        True if code is valid, False otherwise
    """
    try:
        totp = TOTPGenerator(secret)
        return totp.verify(code, window=window)
    except Exception as e:
        logger.error("TOTP verification error", error=str(e))
        return False


def generate_mfa_token(user_id: str, expires_minutes: int = 5) -> str:
    """
    Generate a temporary MFA session token.

    This token is used between password verification and MFA verification
    to maintain the authentication state.

    Args:
        user_id: The user's ID
        expires_minutes: Token expiration time

    Returns:
        Encrypted MFA session token
    """
    from app.core.security import create_access_token
    from datetime import timedelta

    # Create a short-lived token for MFA session
    return create_access_token(
        user_id=user_id,
        tenant_id="mfa",  # Special marker
        role="mfa_pending",
        expires_delta=timedelta(minutes=expires_minutes),
    )


def verify_mfa_token(token: str) -> Optional[str]:
    """
    Verify and decode an MFA session token.

    Args:
        token: The MFA session token

    Returns:
        User ID if valid, None otherwise
    """
    from app.core.security import decode_token

    payload = decode_token(token)
    if payload and payload.role == "mfa_pending":
        return payload.sub
    return None


class MFAManager:
    """
    High-level MFA management for users.
    """

    @staticmethod
    async def setup_mfa(user) -> dict:
        """
        Initialize MFA setup for a user.

        Returns:
            Dict with secret, provisioning URI, and backup codes
        """
        secret = generate_secret()
        backup_codes = generate_backup_codes(settings.MFA_BACKUP_CODES_COUNT)

        # Store hashed backup codes
        hashed_codes = [hash_backup_code(code) for code in backup_codes]

        # Generate provisioning URI
        uri = generate_provisioning_uri(secret, user.email)

        logger.info(
            "MFA setup initiated",
            user_id=str(user.id),
            email=user.email,
        )

        return {
            "secret": secret,
            "provisioning_uri": uri,
            "backup_codes": backup_codes,
            "hashed_backup_codes": hashed_codes,
        }

    @staticmethod
    async def enable_mfa(user, secret: str, code: str, hashed_backup_codes: List[str]) -> bool:
        """
        Enable MFA after verification.

        Args:
            user: The user model
            secret: The TOTP secret
            code: The verification code
            hashed_backup_codes: List of hashed backup codes

        Returns:
            True if MFA was enabled successfully
        """
        if not verify_totp(secret, code):
            return False

        user.mfa_enabled = True
        user.mfa_secret = secret  # Should be encrypted in production
        user.mfa_backup_codes = hashed_backup_codes
        user.mfa_verified_at = datetime.utcnow()

        logger.info(
            "MFA enabled",
            user_id=str(user.id),
            email=user.email,
        )

        return True

    @staticmethod
    async def verify_mfa(user, code: str) -> bool:
        """
        Verify MFA code during login.

        Args:
            user: The user model
            code: The TOTP code

        Returns:
            True if verification successful
        """
        if not user.mfa_enabled or not user.mfa_secret:
            return False

        return verify_totp(user.mfa_secret, code)

    @staticmethod
    async def use_backup_code(user, code: str) -> bool:
        """
        Use a backup code for MFA verification.

        Args:
            user: The user model
            code: The backup code

        Returns:
            True if backup code was valid and used
        """
        if not user.mfa_enabled or not user.mfa_backup_codes:
            return False

        idx = verify_backup_code(code, user.mfa_backup_codes)
        if idx is not None:
            # Remove used backup code
            codes = list(user.mfa_backup_codes)
            codes[idx] = ""  # Mark as used
            user.mfa_backup_codes = codes

            logger.warning(
                "Backup code used",
                user_id=str(user.id),
                remaining_codes=len([c for c in codes if c]),
            )

            return True

        return False

    @staticmethod
    async def disable_mfa(user, password: str, code: str) -> bool:
        """
        Disable MFA for a user.

        Args:
            user: The user model
            password: User's password for verification
            code: Current TOTP code

        Returns:
            True if MFA was disabled
        """
        from app.core.security import verify_password

        if not verify_password(password, user.hashed_password):
            return False

        if not verify_totp(user.mfa_secret, code):
            return False

        user.mfa_enabled = False
        user.mfa_secret = None
        user.mfa_backup_codes = None
        user.mfa_verified_at = None

        logger.info(
            "MFA disabled",
            user_id=str(user.id),
            email=user.email,
        )

        return True

    @staticmethod
    def regenerate_backup_codes(user) -> List[str]:
        """
        Regenerate backup codes for a user.

        Args:
            user: The user model

        Returns:
            New list of backup codes
        """
        backup_codes = generate_backup_codes(settings.MFA_BACKUP_CODES_COUNT)
        hashed_codes = [hash_backup_code(code) for code in backup_codes]
        user.mfa_backup_codes = hashed_codes

        logger.info(
            "Backup codes regenerated",
            user_id=str(user.id),
        )

        return backup_codes
