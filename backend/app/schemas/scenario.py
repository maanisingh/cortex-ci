from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.scenario import ScenarioStatus, ScenarioType


class ScenarioBase(BaseModel):
    """Base scenario schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: ScenarioType


class ScenarioCreate(ScenarioBase):
    """Scenario creation schema."""
    parameters: Dict[str, Any] = {}
    affected_entity_ids: List[str] = []
    cascade_depth: int = Field(1, ge=1, le=5)
    cascade_timeline_days: Optional[int] = Field(None, ge=1, le=365)


class ScenarioUpdate(BaseModel):
    """Scenario update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    cascade_depth: Optional[int] = Field(None, ge=1, le=5)
    cascade_timeline_days: Optional[int] = Field(None, ge=1, le=365)


class ScenarioResponse(ScenarioBase):
    """Scenario response schema."""
    id: UUID
    tenant_id: UUID
    status: ScenarioStatus
    parameters: Dict[str, Any]
    affected_entity_ids: List[str]
    results: Dict[str, Any]
    cascade_depth: int
    cascade_timeline_days: Optional[int]
    cascade_results: Dict[str, Any]
    baseline_snapshot: Dict[str, Any]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_by: Optional[UUID]
    archived_at: Optional[datetime]
    outcome_notes: Optional[str]
    lessons_learned: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScenarioResult(BaseModel):
    """Detailed scenario result."""
    scenario_id: UUID
    status: ScenarioStatus
    summary: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    impacted_entities: List[Dict[str, Any]]
    risk_score_changes: Dict[str, Any]
    cascading_effects: List[Dict[str, Any]]
    recommendations: List[str]
    execution_time_seconds: Optional[float]


class ScenarioListResponse(BaseModel):
    """Paginated scenario list response."""
    items: List[ScenarioResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ScenarioArchiveRequest(BaseModel):
    """Request to archive a scenario with outcome."""
    outcome_notes: Optional[str] = None
    lessons_learned: Optional[str] = None
