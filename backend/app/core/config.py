from pydantic_settings import BaseSettings
from pydantic import Field, validator
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "CORTEX-CI"
    APP_VERSION: str = "3.0.0"  # Phase 3
    APP_DESCRIPTION: str = "Government-grade Constraint Intelligence Platform"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/v1"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/cortex_ci"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Security - Core
    SECRET_KEY: str = Field(
        default="change-this-in-production-use-openssl-rand-hex-32",
        env="SECRET_KEY"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Security - CORS (Phase 3)
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000",
        env="ALLOWED_ORIGINS"
    )
    ALLOWED_HOSTS: str = Field(
        default="localhost,127.0.0.1",
        env="ALLOWED_HOSTS"
    )

    # Security - Rate Limiting (Phase 3)
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE: int = 5
    RATE_LIMIT_EXPORT_REQUESTS_PER_HOUR: int = 10
    RATE_LIMIT_BULK_REQUESTS_PER_HOUR: int = 20

    # Security - MFA (Phase 3)
    MFA_ENABLED: bool = True
    MFA_ISSUER: str = "CORTEX-CI"
    MFA_REQUIRED_FOR_ADMIN: bool = True

    # Security - Encryption (Phase 3)
    ENCRYPTION_KEY: str = Field(
        default="",
        env="ENCRYPTION_KEY"
    )
    ENCRYPT_SENSITIVE_FIELDS: bool = True

    # Security - Password Policy (Phase 3)
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    PASSWORD_MAX_AGE_DAYS: int = 90

    # Security - Session (Phase 3)
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_CONCURRENT_SESSIONS: int = 3
    SESSION_INVALIDATE_ON_PASSWORD_CHANGE: bool = True

    # Security - Audit (Phase 3)
    AUDIT_LOG_RETENTION_DAYS: int = 365
    AUDIT_ARCHIVE_ENABLED: bool = True
    AUDIT_ARCHIVE_PATH: str = "/var/log/cortex-ci/audit-archive"

    # Multi-tenant
    TENANT_HEADER: str = "X-Tenant-ID"
    DEFAULT_TENANT_SLUG: str = "default"

    # Risk Engine
    RISK_CONSTRAINT_WEIGHT: float = 0.30
    RISK_DEPENDENCY_WEIGHT: float = 0.35
    RISK_COUNTRY_WEIGHT: float = 0.20
    RISK_CRITICALITY_WEIGHT: float = 0.15

    # Risk Thresholds
    RISK_THRESHOLD_LOW: float = 40.0
    RISK_THRESHOLD_MEDIUM: float = 60.0
    RISK_THRESHOLD_HIGH: float = 80.0

    # Search (Meilisearch)
    MEILISEARCH_URL: str = Field(
        default="http://meilisearch:7700",
        env="MEILISEARCH_URL"
    )
    MEILISEARCH_API_KEY: str = Field(
        default="",
        env="MEILISEARCH_API_KEY"
    )

    # WebSocket (Phase 4)
    WEBSOCKET_ENABLED: bool = True
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30

    # Export (Phase 4)
    EXPORT_MAX_RECORDS: int = 10000
    EXPORT_TEMP_PATH: str = "/tmp/cortex-exports"

    # Simulation (Phase 5)
    SIMULATION_MAX_DEPTH: int = 10
    SIMULATION_MAX_ENTITIES: int = 1000
    SIMULATION_TIMEOUT_SECONDS: int = 300

    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return v
        return ",".join(v) if v else ""

    def get_allowed_origins_list(self) -> List[str]:
        """Get list of allowed CORS origins."""
        if not self.ALLOWED_ORIGINS:
            return []
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    def get_allowed_hosts_list(self) -> List[str]:
        """Get list of allowed hosts."""
        if not self.ALLOWED_HOSTS:
            return []
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() in ("development", "dev", "local")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
