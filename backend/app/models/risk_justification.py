"""Phase 2.3: Risk Justification Engine - Legal defensibility models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional
from decimal import Decimal

from sqlalchemy import String, Text, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin

if TYPE_CHECKING:
    from app.models.entity import Entity
    from app.models.risk import RiskScore


class RiskJustification(Base, TimestampMixin, TenantMixin):
    """Detailed justification for a risk score - provides legal defensibility."""

    __tablename__ = "risk_justifications"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Link to entity and risk score
    entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    risk_score_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("risk_scores.id", ondelete="SET NULL"),
        nullable=True,
    )

    # The score being justified
    risk_score: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)

    # Primary factors with contributions
    # Format: [{"factor": "country_risk", "contribution": 35.2, "source": "OFAC", "evidence": "..."}]
    primary_factors: Mapped[list] = mapped_column(JSONB, default=list)

    # Documented assumptions
    # Format: ["Country code derived from address", "Name matching uses exact match"]
    assumptions: Mapped[list] = mapped_column(JSONB, default=list)

    # Uncertainty quantification
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.85"))
    uncertainty_factors: Mapped[list] = mapped_column(JSONB, default=list)

    # Source citations
    # Format: [{"source": "OFAC SDN List", "date": "2025-12-23", "record_id": "UN-12345"}]
    source_citations: Mapped[list] = mapped_column(JSONB, default=list)

    # Override capability
    analyst_can_override: Mapped[bool] = mapped_column(Boolean, default=True)
    overridden_by: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    overridden_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    override_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    original_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    # Version tracking for audit
    version: Mapped[int] = mapped_column(default=1)
    previous_version_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )

    # Relationships
    entity: Mapped["Entity"] = relationship("Entity")
    risk_score_obj: Mapped[Optional["RiskScore"]] = relationship("RiskScore")

    def __repr__(self) -> str:
        return f"<RiskJustification entity={self.entity_id} score={self.risk_score}>"

    def to_legal_export(self) -> dict:
        """Generate legal defense documentation format."""
        return {
            "entity_id": str(self.entity_id),
            "risk_score": float(self.risk_score),
            "level": self.risk_level,
            "justification": {
                "primary_factors": self.primary_factors,
                "assumptions": self.assumptions,
                "uncertainty": {
                    "confidence": float(self.confidence),
                    "factors": self.uncertainty_factors,
                },
                "sources": self.source_citations,
                "generated_at": self.created_at.isoformat()
                if self.created_at
                else None,
                "analyst_can_override": self.analyst_can_override,
            },
            "override": {
                "was_overridden": self.overridden_by is not None,
                "overridden_at": self.overridden_at.isoformat()
                if self.overridden_at
                else None,
                "reason": self.override_reason,
                "original_score": float(self.original_score)
                if self.original_score
                else None,
            }
            if self.overridden_by
            else None,
        }
