from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum
from sqlalchemy import String, ForeignKey, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin


class RiskLevel(str, Enum):
    """Risk level classification."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskScore(Base, TimestampMixin, TenantMixin):
    """Calculated risk score for an entity."""

    __tablename__ = "risk_scores"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Related entity
    entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Score (0-100)
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    # Level derived from score
    level: Mapped[RiskLevel] = mapped_column(
        SQLEnum(RiskLevel), nullable=False, index=True
    )

    # Component scores (for transparency)
    direct_match_score: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    indirect_match_score: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    country_risk_score: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    dependency_risk_score: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )

    # Detailed factors (for justification engine - Phase 2)
    factors: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Calculation metadata
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    calculation_version: Mapped[str] = mapped_column(
        String(50), default="1.0", nullable=False
    )

    # Previous score (for change tracking)
    previous_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    previous_level: Mapped[Optional[RiskLevel]] = mapped_column(
        SQLEnum(RiskLevel), nullable=True
    )

    # Relationships
    entity = relationship("Entity", back_populates="risk_scores")

    def __repr__(self) -> str:
        return f"<RiskScore {self.entity_id}: {self.score} ({self.level.value})>"

    @staticmethod
    def score_to_level(score: float) -> RiskLevel:
        """Convert numeric score to risk level."""
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 40:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    @property
    def score_changed(self) -> bool:
        """Check if score changed from previous calculation."""
        return self.previous_score is not None and self.previous_score != self.score

    @property
    def level_changed(self) -> bool:
        """Check if level changed from previous calculation."""
        return self.previous_level is not None and self.previous_level != self.level
