"""Phase 2.4: Institutional Memory - Historical tracking models."""

from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional
from decimal import Decimal

from sqlalchemy import String, Text, ForeignKey, Date, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin

if TYPE_CHECKING:
    from app.models.constraint import Constraint
    from app.models.entity import Entity
    from app.models.user import User


class HistoricalSnapshot(Base, TimestampMixin, TenantMixin):
    """Point-in-time snapshot of an entity's risk state."""

    __tablename__ = "historical_snapshots"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Entity being tracked
    entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Snapshot date
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Risk state at this point
    risk_score: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)

    # Constraints that were active
    constraints_applied: Mapped[list] = mapped_column(
        JSONB, default=list
    )  # List of constraint IDs

    # Dependencies at this time
    dependency_count: Mapped[int] = mapped_column(default=0)
    incoming_dependencies: Mapped[int] = mapped_column(default=0)
    outgoing_dependencies: Mapped[int] = mapped_column(default=0)

    # Entity state snapshot
    entity_data: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    entity: Mapped["Entity"] = relationship("Entity")

    def __repr__(self) -> str:
        return f"<HistoricalSnapshot entity={self.entity_id} date={self.snapshot_date}>"


class DecisionOutcome(Base, TimestampMixin, TenantMixin):
    """Track decisions and their outcomes for institutional learning."""

    __tablename__ = "decision_outcomes"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Decision info
    decision_date: Mapped[date] = mapped_column(Date, nullable=False)
    decision_summary: Mapped[str] = mapped_column(Text, nullable=False)
    decision_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Who made the decision
    decision_maker_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    decision_maker_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    # Entities involved
    entities_involved: Mapped[list] = mapped_column(JSONB, default=list)

    # Context at decision time
    context_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict)
    risk_scores_at_decision: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Outcome tracking
    outcome_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    outcome_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outcome_success: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Lessons learned
    lessons_learned: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[list] = mapped_column(JSONB, default=list)

    # Status
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    decision_maker: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self) -> str:
        return f"<DecisionOutcome {self.decision_type} on {self.decision_date}>"


class ConstraintChange(Base, TimestampMixin, TenantMixin):
    """Track changes to constraints over time."""

    __tablename__ = "constraint_changes"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Which constraint changed
    constraint_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("constraints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Change info
    change_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    change_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # created, updated, deactivated
    change_summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Before/after states
    before_state: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    after_state: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Who made the change
    changed_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Impact analysis
    entities_affected: Mapped[int] = mapped_column(default=0)
    risk_scores_affected: Mapped[int] = mapped_column(default=0)

    # Relationships
    constraint: Mapped["Constraint"] = relationship("Constraint")
    changed_by: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self) -> str:
        return f"<ConstraintChange {self.change_type} on {self.change_date}>"


class TransitionReport(Base, TimestampMixin, TenantMixin):
    """Leadership handoff documentation."""

    __tablename__ = "transition_reports"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Report info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)

    # Content sections
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    key_risks: Mapped[list] = mapped_column(JSONB, default=list)
    critical_entities: Mapped[list] = mapped_column(JSONB, default=list)
    pending_decisions: Mapped[list] = mapped_column(JSONB, default=list)
    lessons_learned: Mapped[list] = mapped_column(JSONB, default=list)
    recommendations: Mapped[list] = mapped_column(JSONB, default=list)

    # Statistics for the period
    statistics: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Metadata
    generated_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_draft: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    generated_by: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self) -> str:
        return (
            f"<TransitionReport {self.title} ({self.period_start} - {self.period_end})>"
        )
