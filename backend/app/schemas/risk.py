from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.risk import RiskLevel, RiskCategory, RiskTreatment, RiskStatus


class RiskScoreResponse(BaseModel):
    """Risk score response schema."""

    id: UUID
    tenant_id: UUID
    entity_id: UUID
    entity_name: str | None = None
    score: float
    level: RiskLevel
    direct_match_score: float
    indirect_match_score: float
    country_risk_score: float
    dependency_risk_score: float
    factors: dict[str, Any]
    calculated_at: datetime
    calculation_version: str
    previous_score: float | None
    previous_level: RiskLevel | None
    score_changed: bool
    level_changed: bool

    class Config:
        from_attributes = True


class RiskSummary(BaseModel):
    """Summary of risk across the organization."""

    total_entities: int
    entities_by_level: dict[str, int]
    average_score: float
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    recent_escalations: int  # Level increased in last 30 days
    recent_improvements: int  # Level decreased in last 30 days


class RiskTrend(BaseModel):
    """Risk trend over time."""

    date: datetime
    average_score: float
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


class RiskCalculateRequest(BaseModel):
    """Request to calculate risk for entities."""

    entity_ids: list[UUID] | None = None  # None means all entities
    force_recalculate: bool = False


class RiskCalculateResponse(BaseModel):
    """Response from risk calculation."""

    calculated: int
    errors: list[dict[str, Any]]


class RiskJustification(BaseModel):
    """Justification for a risk score (Phase 2)."""

    risk_level: RiskLevel
    primary_factors: list[str]
    assumptions: list[str]
    supporting_sources: list[str]
    uncertainty: str
    recommendation: str
    calculation_details: dict[str, Any]


# Risk Register Schemas
class RiskRegisterCreate(BaseModel):
    """Schema for creating a risk register entry."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    category: RiskCategory
    status: RiskStatus = RiskStatus.DRAFT
    likelihood: int = Field(default=3, ge=1, le=5)
    impact: int = Field(default=3, ge=1, le=5)
    residual_likelihood: int | None = Field(None, ge=1, le=5)
    residual_impact: int | None = Field(None, ge=1, le=5)
    treatment: RiskTreatment = RiskTreatment.MONITOR
    treatment_plan: str | None = Field(None, max_length=2000)
    risk_owner_id: UUID | None = None
    risk_owner_name: str | None = None
    entity_id: UUID | None = None
    risk_appetite_threshold: float | None = Field(None, ge=0, le=100)
    review_date: datetime | None = None
    target_closure_date: datetime | None = None
    source: str | None = None
    reference_id: str | None = None
    control_ids: list[UUID] | None = None
    tags: list[str] | None = None
    custom_fields: dict[str, Any] | None = None


class RiskRegisterUpdate(BaseModel):
    """Schema for updating a risk register entry."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    category: RiskCategory | None = None
    status: RiskStatus | None = None
    likelihood: int | None = Field(None, ge=1, le=5)
    impact: int | None = Field(None, ge=1, le=5)
    residual_likelihood: int | None = Field(None, ge=1, le=5)
    residual_impact: int | None = Field(None, ge=1, le=5)
    treatment: RiskTreatment | None = None
    treatment_plan: str | None = Field(None, max_length=2000)
    risk_owner_id: UUID | None = None
    risk_owner_name: str | None = None
    entity_id: UUID | None = None
    risk_appetite_threshold: float | None = Field(None, ge=0, le=100)
    review_date: datetime | None = None
    target_closure_date: datetime | None = None
    closed_date: datetime | None = None
    source: str | None = None
    reference_id: str | None = None
    control_ids: list[UUID] | None = None
    tags: list[str] | None = None
    custom_fields: dict[str, Any] | None = None


class RiskRegisterResponse(BaseModel):
    """Schema for risk register response."""

    id: UUID
    tenant_id: UUID
    risk_id: str
    title: str
    description: str | None
    category: RiskCategory
    status: RiskStatus
    likelihood: int
    impact: int
    inherent_risk_score: float | None
    inherent_risk_level: RiskLevel | None
    residual_likelihood: int | None
    residual_impact: int | None
    residual_risk_score: float | None
    residual_risk_level: RiskLevel | None
    treatment: RiskTreatment
    treatment_plan: str | None
    risk_owner_id: UUID | None
    risk_owner_name: str | None
    entity_id: UUID | None
    entity_name: str | None = None
    risk_appetite_threshold: float | None
    exceeds_appetite: bool
    identified_date: datetime
    review_date: datetime | None
    target_closure_date: datetime | None
    closed_date: datetime | None
    source: str | None
    reference_id: str | None
    control_ids: list[UUID] | None
    tags: list[str] | None
    custom_fields: dict[str, Any] | None
    last_assessed_at: datetime | None
    last_assessed_by: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RiskRegisterList(BaseModel):
    """Paginated list of risk register entries."""

    items: list[RiskRegisterResponse]
    total: int
    page: int
    page_size: int
    pages: int


class RiskRegisterSummary(BaseModel):
    """Summary of the risk register."""

    total_risks: int
    by_category: dict[str, int]
    by_status: dict[str, int]
    by_level: dict[str, int]
    exceeds_appetite_count: int
    overdue_review_count: int
    average_inherent_score: float
    average_residual_score: float | None
