from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "CORTEX-CI"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Government-grade Constraint Intelligence Platform"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/cortex_ci"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Security
    SECRET_KEY: str = "change-this-in-production-use-openssl-rand-hex-32"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

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

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
