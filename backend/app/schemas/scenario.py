from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.scenario import ScenarioStatus, ScenarioType


class ScenarioBase(BaseModel):
    """Base scenario schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    type: ScenarioType


class ScenarioCreate(ScenarioBase):
    """Scenario creation schema."""

    parameters: dict[str, Any] = {}
    affected_entity_ids: list[str] = []
    cascade_depth: int = Field(1, ge=1, le=5)
    cascade_timeline_days: int | None = Field(None, ge=1, le=365)


class ScenarioUpdate(BaseModel):
    """Scenario update schema."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    parameters: dict[str, Any] | None = None
    cascade_depth: int | None = Field(None, ge=1, le=5)
    cascade_timeline_days: int | None = Field(None, ge=1, le=365)


class ScenarioResponse(ScenarioBase):
    """Scenario response schema."""

    id: UUID
    tenant_id: UUID
    status: ScenarioStatus
    parameters: dict[str, Any]
    affected_entity_ids: list[str]
    results: dict[str, Any]
    cascade_depth: int
    cascade_timeline_days: int | None
    cascade_results: dict[str, Any]
    baseline_snapshot: dict[str, Any]
    started_at: datetime | None
    completed_at: datetime | None
    created_by: UUID | None
    archived_at: datetime | None
    outcome_notes: str | None
    lessons_learned: str | None
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
    impacted_entities: list[dict[str, Any]]
    risk_score_changes: dict[str, Any]
    cascading_effects: list[dict[str, Any]]
    recommendations: list[str]
    execution_time_seconds: float | None


class ScenarioListResponse(BaseModel):
    """Paginated scenario list response."""

    items: list[ScenarioResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ScenarioArchiveRequest(BaseModel):
    """Request to archive a scenario with outcome."""

    outcome_notes: str | None = None
    lessons_learned: str | None = None
