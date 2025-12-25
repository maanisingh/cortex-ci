from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.constraint import ConstraintType, ConstraintSeverity


class ConstraintBase(BaseModel):
    """Base constraint schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: ConstraintType
    severity: ConstraintSeverity = ConstraintSeverity.MEDIUM
    reference_code: Optional[str] = None
    source_document: Optional[str] = None
    external_url: Optional[str] = None
    applies_to_entity_types: List[str] = []
    applies_to_countries: List[str] = []
    applies_to_categories: List[str] = []
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    review_date: Optional[date] = None
    risk_weight: float = Field(1.0, ge=0, le=10)
    requirements: Dict[str, Any] = {}
    is_mandatory: bool = True
    tags: List[str] = []
    custom_data: Dict[str, Any] = {}


class ConstraintCreate(ConstraintBase):
    """Constraint creation schema."""

    pass


class ConstraintUpdate(BaseModel):
    """Constraint update schema."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    type: Optional[ConstraintType] = None
    severity: Optional[ConstraintSeverity] = None
    reference_code: Optional[str] = None
    source_document: Optional[str] = None
    external_url: Optional[str] = None
    applies_to_entity_types: Optional[List[str]] = None
    applies_to_countries: Optional[List[str]] = None
    applies_to_categories: Optional[List[str]] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    review_date: Optional[date] = None
    risk_weight: Optional[float] = Field(None, ge=0, le=10)
    requirements: Optional[Dict[str, Any]] = None
    is_mandatory: Optional[bool] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    custom_data: Optional[Dict[str, Any]] = None


class ConstraintResponse(ConstraintBase):
    """Constraint response schema."""

    id: UUID
    tenant_id: UUID
    is_active: bool
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConstraintListResponse(BaseModel):
    """Paginated constraint list response."""

    items: List[ConstraintResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ConstraintSummary(BaseModel):
    """Summary of constraints."""

    total: int
    by_type: Dict[str, int]
    by_severity: Dict[str, int]
    active: int
    expiring_soon: int  # Within 30 days
    mandatory: int
