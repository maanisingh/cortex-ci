from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class TenantBase(BaseModel):
    """Base tenant schema."""

    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = None


class TenantCreate(TenantBase):
    """Tenant creation schema."""

    slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    settings: dict[str, Any] = {}
    risk_weights: dict[str, float] = {
        "direct_match": 0.4,
        "indirect_match": 0.25,
        "country_risk": 0.2,
        "dependency": 0.15,
    }


class TenantUpdate(BaseModel):
    """Tenant update schema."""

    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    settings: dict[str, Any] | None = None
    risk_weights: dict[str, float] | None = None
    is_active: bool | None = None


class TenantResponse(TenantBase):
    """Tenant response schema."""

    id: UUID
    slug: str
    is_active: bool
    settings: dict[str, Any]
    risk_weights: dict[str, float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
