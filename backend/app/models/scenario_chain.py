"""Phase 2.2: Scenario Chains - Cascading effect prediction models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional, List
from enum import Enum
from decimal import Decimal

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    Integer,
    Enum as SQLEnum,
    Boolean,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin

if TYPE_CHECKING:
    from app.models.entity import Entity


class EffectSeverity(str, Enum):
    """Severity of an effect in a scenario chain."""

    NEGLIGIBLE = "negligible"
    MINOR = "minor"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"


class ScenarioChain(Base, TimestampMixin, TenantMixin):
    """Multi-step cascading scenario for impact analysis."""

    __tablename__ = "scenario_chains"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Trigger
    trigger_event: Mapped[str] = mapped_column(Text, nullable=False)
    trigger_entity_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Analysis results
    total_entities_affected: Mapped[int] = mapped_column(Integer, default=0)
    max_cascade_depth: Mapped[int] = mapped_column(Integer, default=0)
    estimated_timeline_days: Mapped[int] = mapped_column(Integer, default=0)
    overall_severity: Mapped[EffectSeverity] = mapped_column(
        SQLEnum(EffectSeverity),
        default=EffectSeverity.MODERATE,
    )

    # Computed risk impact
    total_risk_increase: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00")
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_simulated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    effects: Mapped[List["ChainEffect"]] = relationship(
        "ChainEffect",
        back_populates="scenario_chain",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ScenarioChain {self.name}: {self.trigger_event[:50]}>"


class ChainEffect(Base, TimestampMixin):
    """Individual effect within a scenario chain."""

    __tablename__ = "chain_effects"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Parent chain
    scenario_chain_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("scenario_chains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Affected entity
    entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Effect details
    effect_description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[EffectSeverity] = mapped_column(
        SQLEnum(EffectSeverity), nullable=False
    )

    # Cascade positioning
    cascade_depth: Mapped[int] = mapped_column(Integer, default=1)
    time_delay_days: Mapped[int] = mapped_column(Integer, default=0)  # 0 = immediate

    # Impact metrics
    risk_score_delta: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00")
    )
    probability: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("1.00"),  # 1.00 = 100%
    )

    # Source of this effect (what caused it)
    caused_by_effect_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("chain_effects.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Additional context
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    scenario_chain: Mapped["ScenarioChain"] = relationship(
        "ScenarioChain", back_populates="effects"
    )
    entity: Mapped["Entity"] = relationship("Entity")
    caused_by: Mapped[Optional["ChainEffect"]] = relationship(
        "ChainEffect", remote_side=[id], foreign_keys=[caused_by_effect_id]
    )

    def __repr__(self) -> str:
        return f"<ChainEffect depth={self.cascade_depth} entity={self.entity_id}>"
