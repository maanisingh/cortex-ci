from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class TenantBase(BaseModel):
    """Base tenant schema."""
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None


class TenantCreate(TenantBase):
    """Tenant creation schema."""
    slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    settings: Dict[str, Any] = {}
    risk_weights: Dict[str, float] = {
        "direct_match": 0.4,
        "indirect_match": 0.25,
        "country_risk": 0.2,
        "dependency": 0.15,
    }


class TenantUpdate(BaseModel):
    """Tenant update schema."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    risk_weights: Optional[Dict[str, float]] = None
    is_active: Optional[bool] = None


class TenantResponse(TenantBase):
    """Tenant response schema."""
    id: UUID
    slug: str
    is_active: bool
    settings: Dict[str, Any]
    risk_weights: Dict[str, float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
