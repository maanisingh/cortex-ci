from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TenantMixin, TimestampMixin


class ScenarioStatus(str, Enum):
    """Status of a scenario simulation."""

    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ScenarioType(str, Enum):
    """Type of scenario being simulated."""

    ENTITY_RESTRICTION = "entity_restriction"
    COUNTRY_EMBARGO = "country_embargo"
    SUPPLIER_LOSS = "supplier_loss"
    DEPENDENCY_FAILURE = "dependency_failure"
    CUSTOM = "custom"


class Scenario(Base, TimestampMixin, TenantMixin):
    """What-if scenario simulation model."""

    __tablename__ = "scenarios"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Scenario metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[ScenarioType] = mapped_column(SQLEnum(ScenarioType), nullable=False)
    status: Mapped[ScenarioStatus] = mapped_column(
        SQLEnum(ScenarioStatus), default=ScenarioStatus.DRAFT, nullable=False
    )

    # Scenario parameters (what changes are being simulated)
    parameters: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    """
    Example parameters:
    {
        "type": "entity_sanctioned",
        "target_entity_ids": ["uuid1", "uuid2"],
        "hypothetical_constraints": [
            {"source": "OFAC", "type": "sanction", ...}
        ]
    }
    """

    # Affected entities (input)
    affected_entity_ids: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )

    # Results
    results: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    """
    Example results:
    {
        "impacted_entities": [...],
        "risk_score_changes": {...},
        "cascading_effects": [...],
        "severity": "HIGH",
        "summary": "..."
    }
    """

    # Phase 2: Scenario Chains (cascading effects)
    cascade_depth: Mapped[int] = mapped_column(default=1, nullable=False)
    cascade_timeline_days: Mapped[int | None] = mapped_column(nullable=True)
    cascade_results: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Comparison with baseline
    baseline_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Execution times
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Created by
    created_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Archival (for institutional memory - Phase 2)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    outcome_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    lessons_learned: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f"<Scenario {self.name} ({self.status.value})>"

    @property
    def duration_seconds(self) -> float | None:
        """Calculate execution duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
