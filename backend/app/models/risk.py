from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TenantMixin, TimestampMixin


class RiskLevel(str, Enum):
    """Risk level classification."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskCategory(str, Enum):
    """Risk category classification for GRC."""

    STRATEGIC = "STRATEGIC"
    OPERATIONAL = "OPERATIONAL"
    FINANCIAL = "FINANCIAL"
    COMPLIANCE = "COMPLIANCE"
    TECHNOLOGY = "TECHNOLOGY"
    REPUTATIONAL = "REPUTATIONAL"
    LEGAL = "LEGAL"
    CYBER = "CYBER"
    THIRD_PARTY = "THIRD_PARTY"
    OTHER = "OTHER"


class RiskTreatment(str, Enum):
    """Risk treatment options."""

    ACCEPT = "ACCEPT"
    MITIGATE = "MITIGATE"
    TRANSFER = "TRANSFER"
    AVOID = "AVOID"
    MONITOR = "MONITOR"


class RiskStatus(str, Enum):
    """Risk status in the register."""

    DRAFT = "DRAFT"
    OPEN = "OPEN"
    IN_TREATMENT = "IN_TREATMENT"
    CLOSED = "CLOSED"
    ACCEPTED = "ACCEPTED"


class RiskScore(Base, TimestampMixin, TenantMixin):
    """Calculated risk score for an entity."""

    __tablename__ = "risk_scores"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

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
    level: Mapped[RiskLevel] = mapped_column(SQLEnum(RiskLevel), nullable=False, index=True)

    # Component scores (for transparency)
    direct_match_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    indirect_match_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    country_risk_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    dependency_risk_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)

    # Detailed factors (for justification engine - Phase 2)
    factors: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Calculation metadata
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    calculation_version: Mapped[str] = mapped_column(String(50), default="1.0", nullable=False)

    # Previous score (for change tracking)
    previous_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    previous_level: Mapped[RiskLevel | None] = mapped_column(SQLEnum(RiskLevel), nullable=True)

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


class RiskRegister(Base, TimestampMixin, TenantMixin):
    """Risk Register entry for GRC - represents an identified risk."""

    __tablename__ = "risk_register"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Risk identification
    risk_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # e.g., RISK-2025-001
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # Risk classification
    category: Mapped[RiskCategory] = mapped_column(SQLEnum(RiskCategory), nullable=False, index=True)
    status: Mapped[RiskStatus] = mapped_column(
        SQLEnum(RiskStatus),
        default=RiskStatus.DRAFT,
        nullable=False,
        index=True
    )

    # Risk assessment (1-5 scale for matrix)
    likelihood: Mapped[int] = mapped_column(default=3, nullable=False)  # 1-5
    impact: Mapped[int] = mapped_column(default=3, nullable=False)  # 1-5
    inherent_risk_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)  # calculated
    inherent_risk_level: Mapped[RiskLevel | None] = mapped_column(SQLEnum(RiskLevel), nullable=True)

    # Residual risk (after controls)
    residual_likelihood: Mapped[int | None] = mapped_column(nullable=True)  # 1-5
    residual_impact: Mapped[int | None] = mapped_column(nullable=True)  # 1-5
    residual_risk_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    residual_risk_level: Mapped[RiskLevel | None] = mapped_column(SQLEnum(RiskLevel), nullable=True)

    # Risk response
    treatment: Mapped[RiskTreatment] = mapped_column(
        SQLEnum(RiskTreatment),
        default=RiskTreatment.MONITOR,
        nullable=False
    )
    treatment_plan: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # Risk ownership
    risk_owner_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    risk_owner_name: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Denormalized for display

    # Related entity (optional - risk may be org-wide)
    entity_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Risk appetite threshold
    risk_appetite_threshold: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    exceeds_appetite: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Dates
    identified_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    review_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    target_closure_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Source and references
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)  # e.g., Audit, Assessment, Incident
    reference_id: Mapped[str | None] = mapped_column(String(100), nullable=True)  # External reference

    # Linked controls
    control_ids: Mapped[list | None] = mapped_column(JSONB, default=list, nullable=True)

    # Tags and metadata
    tags: Mapped[list | None] = mapped_column(JSONB, default=list, nullable=True)
    custom_fields: Mapped[dict | None] = mapped_column(JSONB, default=dict, nullable=True)

    # Audit trail
    last_assessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_assessed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    entity = relationship("Entity", backref="risks")
    risk_owner = relationship("User", backref="owned_risks")

    def __repr__(self) -> str:
        return f"<RiskRegister {self.risk_id}: {self.title} ({self.status.value})>"

    def calculate_inherent_score(self) -> float:
        """Calculate inherent risk score from likelihood * impact."""
        score = (self.likelihood * self.impact) * 4  # Scale to 0-100
        self.inherent_risk_score = min(score, 100)
        self.inherent_risk_level = RiskScore.score_to_level(self.inherent_risk_score)
        return self.inherent_risk_score

    def calculate_residual_score(self) -> float | None:
        """Calculate residual risk score if residual values are set."""
        if self.residual_likelihood and self.residual_impact:
            score = (self.residual_likelihood * self.residual_impact) * 4
            self.residual_risk_score = min(score, 100)
            self.residual_risk_level = RiskScore.score_to_level(self.residual_risk_score)
            return self.residual_risk_score
        return None

    def check_appetite(self) -> bool:
        """Check if risk exceeds appetite threshold."""
        if self.risk_appetite_threshold and self.residual_risk_score:
            self.exceeds_appetite = self.residual_risk_score > self.risk_appetite_threshold
        elif self.risk_appetite_threshold and self.inherent_risk_score:
            self.exceeds_appetite = self.inherent_risk_score > self.risk_appetite_threshold
        return self.exceeds_appetite
