from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel

from app.models.risk import RiskLevel


class RiskScoreResponse(BaseModel):
    """Risk score response schema."""

    id: UUID
    tenant_id: UUID
    entity_id: UUID
    entity_name: Optional[str] = None
    score: float
    level: RiskLevel
    direct_match_score: float
    indirect_match_score: float
    country_risk_score: float
    dependency_risk_score: float
    factors: Dict[str, Any]
    calculated_at: datetime
    calculation_version: str
    previous_score: Optional[float]
    previous_level: Optional[RiskLevel]
    score_changed: bool
    level_changed: bool

    class Config:
        from_attributes = True


class RiskSummary(BaseModel):
    """Summary of risk across the organization."""

    total_entities: int
    entities_by_level: Dict[str, int]
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

    entity_ids: Optional[List[UUID]] = None  # None means all entities
    force_recalculate: bool = False


class RiskCalculateResponse(BaseModel):
    """Response from risk calculation."""

    calculated: int
    errors: List[Dict[str, Any]]


class RiskJustification(BaseModel):
    """Justification for a risk score (Phase 2)."""

    risk_level: RiskLevel
    primary_factors: List[str]
    assumptions: List[str]
    supporting_sources: List[str]
    uncertainty: str
    recommendation: str
    calculation_details: Dict[str, Any]
