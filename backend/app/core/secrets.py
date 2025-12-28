"""
Secrets Management Module (Phase 3.4)
Implements secure secrets storage, encryption, and rotation.
"""

import base64
import hashlib
import secrets as py_secrets
from datetime import datetime, timedelta
from typing import Any

import structlog
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings

logger = structlog.get_logger()


class SecretsManager:
    """
    Secure secrets management with encryption at rest.
    Uses Fernet symmetric encryption with key derivation.
    """

    def __init__(self, master_key: str | None = None):
        """
        Initialize secrets manager.

        Args:
            master_key: Master encryption key (from environment or config)
        """
        self._master_key = master_key or settings.ENCRYPTION_KEY
        self._fernet: Fernet | None = None
        self._secrets_cache: dict[str, dict[str, Any]] = {}
        self._init_encryption()

    def _init_encryption(self):
        """Initialize Fernet encryption with derived key."""
        if not self._master_key:
            logger.warning("No encryption key configured, secrets will not be encrypted")
            return

        try:
            # Use PBKDF2 to derive a key from the master key
            salt = hashlib.sha256(b"cortex-ci-secrets-salt").digest()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self._master_key.encode()))
            self._fernet = Fernet(key)
            logger.info("Secrets encryption initialized")
        except Exception as e:
            logger.error("Failed to initialize encryption", error=str(e))

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.

        Args:
            plaintext: The string to encrypt

        Returns:
            Base64 encoded encrypted string
        """
        if not self._fernet:
            logger.warning("Encryption not available, storing plaintext")
            return plaintext

        try:
            encrypted = self._fernet.encrypt(plaintext.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error("Encryption failed", error=str(e))
            raise ValueError("Failed to encrypt data")

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted string.

        Args:
            ciphertext: Base64 encoded encrypted string

        Returns:
            Decrypted plaintext
        """
        if not self._fernet:
            logger.warning("Encryption not available, returning as-is")
            return ciphertext

        try:
            encrypted = base64.b64decode(ciphertext.encode())
            decrypted = self._fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            logger.error("Decryption failed", error=str(e))
            raise ValueError("Failed to decrypt data")

    def store_secret(
        self,
        name: str,
        value: str,
        metadata: dict[str, Any] | None = None,
        expires_at: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Store a secret with optional expiration.

        Args:
            name: Secret name/identifier
            value: Secret value (will be encrypted)
            metadata: Optional metadata about the secret
            expires_at: Optional expiration datetime

        Returns:
            Secret metadata (without the actual value)
        """
        encrypted_value = self.encrypt(value)

        secret_entry = {
            "name": name,
            "encrypted_value": encrypted_value,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else None,
            "version": 1,
        }

        # Check if updating existing secret
        if name in self._secrets_cache:
            secret_entry["version"] = self._secrets_cache[name]["version"] + 1
            logger.info("Secret updated", name=name, version=secret_entry["version"])
        else:
            logger.info("Secret created", name=name)

        self._secrets_cache[name] = secret_entry

        return {
            "name": name,
            "created_at": secret_entry["created_at"],
            "expires_at": secret_entry["expires_at"],
            "version": secret_entry["version"],
        }

    def get_secret(self, name: str) -> str | None:
        """
        Retrieve a secret value.

        Args:
            name: Secret name/identifier

        Returns:
            Decrypted secret value or None if not found/expired
        """
        if name not in self._secrets_cache:
            logger.warning("Secret not found", name=name)
            return None

        entry = self._secrets_cache[name]

        # Check expiration
        if entry.get("expires_at"):
            expires = datetime.fromisoformat(entry["expires_at"])
            if datetime.utcnow() > expires:
                logger.warning("Secret expired", name=name)
                return None

        try:
            return self.decrypt(entry["encrypted_value"])
        except Exception:
            logger.error("Failed to decrypt secret", name=name)
            return None

    def delete_secret(self, name: str) -> bool:
        """
        Delete a secret.

        Args:
            name: Secret name/identifier

        Returns:
            True if deleted, False if not found
        """
        if name in self._secrets_cache:
            del self._secrets_cache[name]
            logger.info("Secret deleted", name=name)
            return True
        return False

    def list_secrets(self) -> list:
        """
        List all stored secrets (metadata only).

        Returns:
            List of secret metadata (without values)
        """
        result = []
        for name, entry in self._secrets_cache.items():
            result.append(
                {
                    "name": name,
                    "created_at": entry["created_at"],
                    "expires_at": entry["expires_at"],
                    "version": entry["version"],
                    "metadata": entry["metadata"],
                }
            )
        return result

    def rotate_secret(
        self,
        name: str,
        new_value: str,
        retain_versions: int = 3,
    ) -> dict[str, Any]:
        """
        Rotate a secret to a new value.

        Args:
            name: Secret name/identifier
            new_value: New secret value
            retain_versions: Number of old versions to retain

        Returns:
            Updated secret metadata
        """
        if name not in self._secrets_cache:
            raise ValueError(f"Secret '{name}' not found")

        old_entry = self._secrets_cache[name]
        metadata = old_entry.get("metadata", {})

        # Track rotation history
        rotation_history = metadata.get("rotation_history", [])
        rotation_history.append(
            {
                "version": old_entry["version"],
                "rotated_at": datetime.utcnow().isoformat(),
            }
        )

        # Keep only recent history
        if len(rotation_history) > retain_versions:
            rotation_history = rotation_history[-retain_versions:]

        metadata["rotation_history"] = rotation_history
        metadata["last_rotated"] = datetime.utcnow().isoformat()

        return self.store_secret(name, new_value, metadata, None)

    @staticmethod
    def generate_secret(length: int = 32) -> str:
        """
        Generate a cryptographically secure random secret.

        Args:
            length: Number of random bytes

        Returns:
            Hex-encoded random string
        """
        return py_secrets.token_hex(length)

    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a formatted API key.

        Returns:
            API key in format 'cortex_xxxxxxxxxxxxx'
        """
        random_part = py_secrets.token_urlsafe(32)
        return f"cortex_{random_part}"


class FieldEncryption:
    """
    Field-level encryption for database columns.
    Used to encrypt sensitive fields before storage.
    """

    def __init__(self, secrets_manager: SecretsManager | None = None):
        self._manager = secrets_manager or secrets_manager_instance

    def encrypt_field(self, value: Any) -> str | None:
        """Encrypt a field value."""
        if value is None:
            return None
        return self._manager.encrypt(str(value))

    def decrypt_field(self, encrypted_value: str | None) -> str | None:
        """Decrypt a field value."""
        if encrypted_value is None:
            return None
        return self._manager.decrypt(encrypted_value)

    def encrypt_dict(self, data: dict[str, Any], fields: list) -> dict[str, Any]:
        """
        Encrypt specific fields in a dictionary.

        Args:
            data: Dictionary containing data
            fields: List of field names to encrypt

        Returns:
            Dictionary with encrypted fields
        """
        result = data.copy()
        for field in fields:
            if field in result and result[field] is not None:
                result[field] = self.encrypt_field(result[field])
        return result

    def decrypt_dict(self, data: dict[str, Any], fields: list) -> dict[str, Any]:
        """
        Decrypt specific fields in a dictionary.

        Args:
            data: Dictionary containing encrypted data
            fields: List of field names to decrypt

        Returns:
            Dictionary with decrypted fields
        """
        result = data.copy()
        for field in fields:
            if field in result and result[field] is not None:
                result[field] = self.decrypt_field(result[field])
        return result


class APIKeyManager:
    """
    Manage API keys for service-to-service authentication.
    """

    def __init__(self, secrets_manager: SecretsManager | None = None):
        self._manager = secrets_manager or secrets_manager_instance
        self._api_keys: dict[str, dict[str, Any]] = {}

    def create_api_key(
        self,
        name: str,
        scopes: list,
        expires_days: int = 365,
    ) -> dict[str, str]:
        """
        Create a new API key.

        Args:
            name: Key name/identifier
            scopes: List of permission scopes
            expires_days: Days until expiration

        Returns:
            Dict containing the API key (shown only once)
        """
        api_key = SecretsManager.generate_api_key()
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(days=expires_days)

        self._api_keys[key_hash] = {
            "name": name,
            "scopes": scopes,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat(),
            "last_used": None,
        }

        logger.info("API key created", name=name, expires_at=expires_at.isoformat())

        return {
            "name": name,
            "api_key": api_key,  # Only shown once
            "expires_at": expires_at.isoformat(),
        }

    def validate_api_key(self, api_key: str) -> dict[str, Any] | None:
        """
        Validate an API key.

        Args:
            api_key: The API key to validate

        Returns:
            Key metadata if valid, None otherwise
        """
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        if key_hash not in self._api_keys:
            return None

        key_data = self._api_keys[key_hash]

        # Check expiration
        expires = datetime.fromisoformat(key_data["expires_at"])
        if datetime.utcnow() > expires:
            logger.warning("API key expired", name=key_data["name"])
            return None

        # Update last used
        key_data["last_used"] = datetime.utcnow().isoformat()

        return {
            "name": key_data["name"],
            "scopes": key_data["scopes"],
        }

    def revoke_api_key(self, name: str) -> bool:
        """
        Revoke an API key by name.

        Args:
            name: Key name to revoke

        Returns:
            True if revoked, False if not found
        """
        for key_hash, data in list(self._api_keys.items()):
            if data["name"] == name:
                del self._api_keys[key_hash]
                logger.info("API key revoked", name=name)
                return True
        return False

    def list_api_keys(self) -> list:
        """List all API keys (metadata only)."""
        return [
            {
                "name": data["name"],
                "scopes": data["scopes"],
                "created_at": data["created_at"],
                "expires_at": data["expires_at"],
                "last_used": data["last_used"],
            }
            for data in self._api_keys.values()
        ]


# Global instances
secrets_manager_instance = SecretsManager()
field_encryption = FieldEncryption()
api_key_manager = APIKeyManager()
