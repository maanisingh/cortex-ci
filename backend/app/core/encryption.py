"""
Data Encryption at Rest Module (Phase 3.5)
Implements field-level encryption for sensitive database columns.
"""

import base64
from typing import Optional, TypeVar, Callable
from functools import wraps
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import structlog

from app.core.config import settings

logger = structlog.get_logger()

T = TypeVar('T')


class DataEncryption:
    """
    Provides encryption/decryption for sensitive data at rest.
    Uses Fernet (AES-128-CBC) symmetric encryption.
    """

    _instance: Optional["DataEncryption"] = None
    _fernet: Optional[Fernet] = None

    def __new__(cls):
        """Singleton pattern for consistent encryption key."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize encryption with key from settings."""
        if not settings.ENCRYPTION_KEY:
            logger.warning("ENCRYPTION_KEY not set, encryption disabled")
            return

        try:
            # Derive a Fernet key from the master key
            salt = b"cortex-ci-data-encryption-v1"
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=150000,
            )
            key = base64.urlsafe_b64encode(
                kdf.derive(settings.ENCRYPTION_KEY.encode())
            )
            self._fernet = Fernet(key)
            logger.info("Data encryption initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize data encryption", error=str(e))
            self._fernet = None

    @property
    def is_enabled(self) -> bool:
        """Check if encryption is enabled."""
        return self._fernet is not None and settings.ENCRYPT_SENSITIVE_FIELDS

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string value.

        Args:
            plaintext: The string to encrypt

        Returns:
            Encrypted string prefixed with 'enc:' marker
        """
        if not self.is_enabled:
            return plaintext

        try:
            encrypted = self._fernet.encrypt(plaintext.encode())
            # Prefix with marker to identify encrypted data
            return f"enc:{base64.urlsafe_b64encode(encrypted).decode()}"
        except Exception as e:
            logger.error("Encryption failed", error=str(e))
            return plaintext

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted string.

        Args:
            ciphertext: The encrypted string (with 'enc:' prefix)

        Returns:
            Decrypted plaintext
        """
        if not self.is_enabled:
            return ciphertext

        # Check for encryption marker
        if not ciphertext.startswith("enc:"):
            # Not encrypted, return as-is
            return ciphertext

        try:
            encrypted = base64.urlsafe_b64decode(ciphertext[4:].encode())
            return self._fernet.decrypt(encrypted).decode()
        except InvalidToken:
            logger.error("Decryption failed - invalid token")
            raise ValueError("Invalid encrypted data")
        except Exception as e:
            logger.error("Decryption failed", error=str(e))
            raise ValueError(f"Decryption error: {str(e)}")

    def encrypt_dict_fields(
        self,
        data: dict,
        fields: list,
    ) -> dict:
        """
        Encrypt specific fields in a dictionary.

        Args:
            data: Dictionary with data
            fields: List of field names to encrypt

        Returns:
            Dictionary with encrypted fields
        """
        result = data.copy()
        for field in fields:
            if field in result and result[field] is not None:
                if isinstance(result[field], str):
                    result[field] = self.encrypt(result[field])
                elif isinstance(result[field], (int, float)):
                    result[field] = self.encrypt(str(result[field]))
        return result

    def decrypt_dict_fields(
        self,
        data: dict,
        fields: list,
    ) -> dict:
        """
        Decrypt specific fields in a dictionary.

        Args:
            data: Dictionary with encrypted data
            fields: List of field names to decrypt

        Returns:
            Dictionary with decrypted fields
        """
        result = data.copy()
        for field in fields:
            if field in result and result[field] is not None:
                if isinstance(result[field], str) and result[field].startswith("enc:"):
                    result[field] = self.decrypt(result[field])
        return result


# Sensitive fields that should be encrypted
SENSITIVE_FIELDS = [
    "ssn",
    "tax_id",
    "bank_account",
    "credit_card",
    "api_key",
    "secret_key",
    "password_hash",
    "mfa_secret",
    "backup_codes",
    "private_key",
    "access_token",
    "refresh_token",
]


class EncryptedString:
    """
    SQLAlchemy type decorator for encrypted string columns.
    Automatically encrypts on write and decrypts on read.
    """

    def __init__(self, encryption: Optional[DataEncryption] = None):
        self._encryption = encryption or data_encryption

    def process_bind_param(self, value: Optional[str], _dialect) -> Optional[str]:
        """Encrypt value before storing in database."""
        if value is None:
            return None
        return self._encryption.encrypt(value)

    def process_result_value(self, value: Optional[str], _dialect) -> Optional[str]:
        """Decrypt value when reading from database."""
        if value is None:
            return None
        return self._encryption.decrypt(value)


def encrypt_on_store(field_names: list):
    """
    Decorator to encrypt specific fields before storing.

    Usage:
        @encrypt_on_store(['ssn', 'tax_id'])
        async def create_entity(data: dict):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find and encrypt data argument
            for i, arg in enumerate(args):
                if isinstance(arg, dict):
                    args = list(args)
                    args[i] = data_encryption.encrypt_dict_fields(arg, field_names)
                    args = tuple(args)
                    break

            for key, value in kwargs.items():
                if isinstance(value, dict):
                    kwargs[key] = data_encryption.encrypt_dict_fields(value, field_names)

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def decrypt_on_load(field_names: list):
    """
    Decorator to decrypt specific fields after loading.

    Usage:
        @decrypt_on_load(['ssn', 'tax_id'])
        async def get_entity(id: str):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            if isinstance(result, dict):
                return data_encryption.decrypt_dict_fields(result, field_names)
            elif hasattr(result, '__dict__'):
                for field in field_names:
                    if hasattr(result, field):
                        value = getattr(result, field)
                        if value and isinstance(value, str):
                            setattr(result, field, data_encryption.decrypt(value))
            return result
        return wrapper
    return decorator


class SecureDataMixin:
    """
    Mixin for SQLAlchemy models with encrypted fields.

    Usage:
        class SensitiveEntity(Base, SecureDataMixin):
            _encrypted_fields = ['ssn', 'tax_id']
            ssn = Column(String)
            tax_id = Column(String)
    """

    _encrypted_fields: list = []

    def encrypt_sensitive_fields(self):
        """Encrypt all sensitive fields before save."""
        for field in self._encrypted_fields:
            value = getattr(self, field, None)
            if value and not value.startswith("enc:"):
                setattr(self, field, data_encryption.encrypt(value))

    def decrypt_sensitive_fields(self):
        """Decrypt all sensitive fields after load."""
        for field in self._encrypted_fields:
            value = getattr(self, field, None)
            if value and value.startswith("enc:"):
                setattr(self, field, data_encryption.decrypt(value))


def mask_sensitive_data(value: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data for display purposes.

    Args:
        value: The sensitive value
        visible_chars: Number of characters to show at the end

    Returns:
        Masked string (e.g., '****1234')
    """
    if not value or len(value) <= visible_chars:
        return "****"
    return "*" * (len(value) - visible_chars) + value[-visible_chars:]


def hash_for_comparison(value: str) -> str:
    """
    Create a hash for comparison without storing the actual value.
    Useful for searching encrypted fields.

    Args:
        value: The value to hash

    Returns:
        Hex-encoded SHA-256 hash
    """
    import hashlib
    return hashlib.sha256(value.encode()).hexdigest()


# Global encryption instance
data_encryption = DataEncryption()


def get_encryption_status() -> dict:
    """Get current encryption status for health checks."""
    return {
        "encryption_enabled": data_encryption.is_enabled,
        "algorithm": "AES-128-CBC (Fernet)",
        "key_derivation": "PBKDF2-HMAC-SHA256",
        "iterations": 150000,
    }
