from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.constraint import ConstraintSeverity, ConstraintType


class ConstraintBase(BaseModel):
    """Base constraint schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    type: ConstraintType
    severity: ConstraintSeverity = ConstraintSeverity.MEDIUM
    reference_code: str | None = None
    source_document: str | None = None
    external_url: str | None = None
    applies_to_entity_types: list[str] = []
    applies_to_countries: list[str] = []
    applies_to_categories: list[str] = []
    effective_date: date | None = None
    expiry_date: date | None = None
    review_date: date | None = None
    risk_weight: float = Field(1.0, ge=0, le=10)
    requirements: dict[str, Any] = {}
    is_mandatory: bool = True
    tags: list[str] = []
    custom_data: dict[str, Any] = {}


class ConstraintCreate(ConstraintBase):
    """Constraint creation schema."""

    pass


class ConstraintUpdate(BaseModel):
    """Constraint update schema."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    type: ConstraintType | None = None
    severity: ConstraintSeverity | None = None
    reference_code: str | None = None
    source_document: str | None = None
    external_url: str | None = None
    applies_to_entity_types: list[str] | None = None
    applies_to_countries: list[str] | None = None
    applies_to_categories: list[str] | None = None
    effective_date: date | None = None
    expiry_date: date | None = None
    review_date: date | None = None
    risk_weight: float | None = Field(None, ge=0, le=10)
    requirements: dict[str, Any] | None = None
    is_mandatory: bool | None = None
    is_active: bool | None = None
    tags: list[str] | None = None
    custom_data: dict[str, Any] | None = None


class ConstraintResponse(ConstraintBase):
    """Constraint response schema."""

    id: UUID
    tenant_id: UUID
    is_active: bool
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConstraintListResponse(BaseModel):
    """Paginated constraint list response."""

    items: list[ConstraintResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ConstraintSummary(BaseModel):
    """Summary of constraints."""

    total: int
    by_type: dict[str, int]
    by_severity: dict[str, int]
    active: int
    expiring_soon: int  # Within 30 days
    mandatory: int
